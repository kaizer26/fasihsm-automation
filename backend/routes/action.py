import os
import json
import re
import threading
from datetime import datetime
from flask import Blueprint, request, jsonify, send_file
import pandas as pd
from api_client import api_client
from selenium_manager import selenium_manager
from session_manager import session_manager
from utils import extract_answers, parse_assignment_status, get_status_keberadaan
from config import Config

action_bp = Blueprint('action', __name__)

# Store for task progress
task_progress = {}


def smart_sort_columns(columns: list) -> list:
    """
    Sort columns with smart ordering for questionnaire format:
    - rXXX format: r + block + question + sub-letter + #item
    - Example: r101, r102a, r102b, r201, r601#1, r601#2, r601#10
    """
    def parse_column(col):
        # Handle non-r columns (put at beginning)
        if not col.startswith('r') or not col[1:2].isdigit():
            # Special columns go first
            priority_cols = ['assignment_id', 'smallcode', 'status_assignment', 'link_preview']
            if col in priority_cols:
                return (0, priority_cols.index(col), 0, '', 0, col)
            return (1, 0, 0, '', 0, col)
        
        # Parse r-columns: r{block}{question}{sub}#{item}
        match = re.match(r'^r(\d)(\d{2,3})([a-z]?\d?)(?:#(\d+))?(.*)$', col, re.IGNORECASE)
        
        if match:
            block = int(match.group(1))
            question = int(match.group(2))
            sub = match.group(3) or ''
            item = int(match.group(4)) if match.group(4) else 0
            suffix = match.group(5) or ''
            return (2, block, question, sub, item, suffix)
        
        # Fallback: just return column name for alphabetical
        return (3, 0, 0, '', 0, col)
    
    return sorted(columns, key=parse_column)


def get_all_smallcodes(group_id: str, kab_id: str, level_region: list) -> list:
    """Get all smallcodes for a kabupaten"""
    smallcodes = []
    
    kecamatan_list = api_client.get_kecamatan(group_id, kab_id)
    
    for kec in kecamatan_list:
        if len(level_region) == 3:
            smallcodes.append(kec['fullCode'])
            continue
            
        desa_list = api_client.get_desa(group_id, kec['id'])
        
        for desa in desa_list:
            if len(level_region) == 4:
                smallcodes.append(desa['fullCode'])
                continue
                
            sls_list = api_client.get_sls(group_id, desa['id'])
            
            for sls in sls_list:
                if len(level_region) == 5:
                    smallcodes.append(sls['fullCode'])
                    continue
                    
                subsls_list = api_client.get_subsls(group_id, sls['id'])
                for subsls in subsls_list:
                    smallcodes.append(subsls['fullCode'])
    
    return smallcodes


def load_cached_wilayah(survey_id: str, period_id: str, kab_id: str) -> list:
    """Load smallcodes from cached wilayah file"""
    filename = f"wilayah_{survey_id}_{period_id}_{kab_id}.json"
    filepath = os.path.join(Config.WILAYAH_DIR, filename)
    
    if os.path.exists(filepath):
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return [item['smallcode'] for item in data.get('smallcodes', [])]
    
    return None


def download_raw_data_task(task_id: str, survey_id: str, period_id: str, template_id: str, 
                           group_id: str, kab_id: str, kab_name: str, survey_name: str, period_name: str):
    """Background task for downloading raw data"""
    try:
        task_progress[task_id] = {
            'status': 'running',
            'progress': 0,
            'message': 'Loading wilayah data...',
            'filename': None,
            'logs': [],
            'total_assignments': 0
        }
        
        # Try to load from cache first
        smallcodes = load_cached_wilayah(survey_id, period_id, kab_id)
        
        if smallcodes:
            task_progress[task_id]['logs'].append('📁 Using cached wilayah data')
        else:
            # Fallback: fetch from API
            task_progress[task_id]['message'] = 'Fetching smallcodes from API...'
            task_progress[task_id]['logs'].append('📍 Fetching smallcodes from kabupaten...')
            
            metadata = api_client.get_region_metadata(group_id)
            level_region = metadata.get('data', {}).get('level', [])
            smallcodes = get_all_smallcodes(group_id, kab_id, level_region)
        
        total = len(smallcodes)
        task_progress[task_id]['logs'].append(f'Found {total} smallcodes')
        
        res_list = []
        assign_list = []
        
        for i, smallcode in enumerate(smallcodes):
            task_progress[task_id]['progress'] = int((i / total) * 100)
            task_progress[task_id]['message'] = f'Processing {smallcode}...'
            
            assignments = api_client.get_assignments_by_smallcode(period_id, smallcode)
            
            if not assignments:
                continue
                
            task_progress[task_id]['total_assignments'] += len(assignments)
            assign_list.extend(assignments)
            
            for assign in assignments:
                assignment_id = assign['assignmentId']
                review_url = f'https://fasih-sm.bps.go.id/survey-collection/survey-review/{assignment_id}/{template_id}/{period_id}/a/1'
                
                try:
                    detail = api_client.get_assignment_detail(assignment_id)
                    inner_json = json.loads(detail['data']['data'])
                    answers = inner_json.get('answers', [])
                    answer_values = extract_answers(answers)
                    
                    # Get status
                    history = api_client.get_assignment_history(assignment_id)
                    status_list = parse_assignment_status(history)
                    status_assignment = status_list[-1]['status_assignment'] if status_list else 'Open'
                    
                    answer_values['assignment_id'] = assignment_id
                    answer_values['link_preview'] = review_url
                    answer_values['status_assignment'] = status_assignment
                    answer_values['smallcode'] = smallcode
                    
                    res_list.append(answer_values)
                except Exception as e:
                    task_progress[task_id]['logs'].append(f'⚠️ Error {assignment_id}: {str(e)}')
            
            task_progress[task_id]['logs'].append(f'✅ {smallcode}: {len(assignments)} assignments')
        
        # Save to Excel
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"Raw_Data_{kab_name}_{survey_name}_{period_name}_{timestamp}.xlsx"
        os.makedirs(Config.RAW_DATA_DIR, exist_ok=True)
        filepath = os.path.join(Config.RAW_DATA_DIR, filename)
        
        if res_list:
            df = pd.DataFrame(res_list)
            
            # Remove duplicate columns
            df = df.loc[:, ~df.columns.duplicated()]
            
            # Get selected columns from task_progress (set by route)
            selected_columns = task_progress[task_id].get('selected_columns', [])
            
            if selected_columns:
                # Filter to only selected columns that exist
                existing_cols = [c for c in selected_columns if c in df.columns]
                df = df[existing_cols]
            else:
                # Sort columns with smart ordering if no selection
                df = df.reindex(smart_sort_columns(list(df.columns)), axis=1)
            
            df.fillna('', inplace=True)
            df.to_excel(filepath, index=False)
            
            task_progress[task_id]['status'] = 'completed'
            task_progress[task_id]['progress'] = 100
            task_progress[task_id]['message'] = f'Completed! {len(res_list)} records saved.'
            task_progress[task_id]['filename'] = filename
            task_progress[task_id]['columns'] = list(df.columns)
            task_progress[task_id]['logs'].append(f'📁 File saved: {filename} ({len(df.columns)} columns)')
        else:
            task_progress[task_id]['status'] = 'completed'
            task_progress[task_id]['progress'] = 100
            task_progress[task_id]['message'] = 'No data found'
            
        # Save session after action
        sess_data = selenium_manager.get_session_data()
        if sess_data['is_logged_in'] and sess_data['username']:
            session_manager.save_session(
                username=sess_data['username'],
                password=sess_data['password'],
                cookies=sess_data['cookies'],
                headers=sess_data['headers']
            )
            task_progress[task_id]['logs'].append('✅ Session updated')
            
    except Exception as e:
        task_progress[task_id]['status'] = 'error'
        task_progress[task_id]['message'] = str(e)
        task_progress[task_id]['logs'].append(f'❌ Error: {str(e)}')


def approve_task(task_id: str, survey_id: str, period_id: str, template_id: str,
                 group_id: str, kab_id: str, kab_name: str, survey_name: str, period_name: str,
                 action_type: str = 'approve'):
    """Background task for approve/revoke/reject"""
    try:
        task_progress[task_id] = {
            'status': 'running',
            'progress': 0,
            'message': 'Getting user role...',
            'filename': None,
            'logs': [],
            'success_count': 0,
            'fail_count': 0,
            'skip_count': 0,
            'total_assignments': 0
        }
        
        # Get role
        role = api_client.get_user_role(period_id)
        task_progress[task_id]['logs'].append(f'👤 Role: {role}')
        
        # Try to load from cache first
        smallcodes = load_cached_wilayah(survey_id, period_id, kab_id)
        
        if smallcodes:
            task_progress[task_id]['logs'].append('📁 Using cached wilayah data')
        else:
            # Fallback: fetch from API
            task_progress[task_id]['message'] = 'Fetching smallcodes from API...'
            metadata = api_client.get_region_metadata(group_id)
            level_region = metadata.get('data', {}).get('level', [])
            smallcodes = get_all_smallcodes(group_id, kab_id, level_region)
        
        total = len(smallcodes)
        
        log_data = []
        button_map = {
            'approve': 'buttonApprove',
            'revoke': 'buttonRevoke',
            'reject': 'buttonReject'
        }
        button_id = button_map.get(action_type, 'buttonApprove')
        
        # Status conditions for each role and action
        # Refactored from fasih_sm_scrape - v6 (1).py
        status_conditions = {
            'approve': {
                'Pengawas': ['SUBMITTED BY Pencacah'],
                'PML': ['SUBMITTED BY PPL'],
                'Admin Kabupaten': ['APPROVED BY Pengawas', 'APPROVED BY PML', 'EDITED BY Admin Kabupaten'],
                'Admin Provinsi': ['COMPLETED BY Admin Kabupaten']
            },
            'revoke': {
                'Pengawas': ['COMPLETED BY Pengawas'],
                # Original script has condition: roles == 'Pengawas' and status_assignment == 'COMPLETED BY Pengawas' and status_keberadaan == '3. Tidak Ditemukan'
                # For revoke purposes, current implementation allows Admin Kabupaten too if needed, but we follow original strictly
            },
            'reject': {
                'Pengawas': ['SUBMITTED BY Pencacah'],
                # Original script: roles == 'Pengawas' and status_assignment == 'SUBMITTED BY Pencacah' and status_keberadaan == '3. Tidak Ditemukan'
            }
        }
        
        allowed_statuses = status_conditions.get(action_type, {}).get(role, [])
        
        # Explicitly defined statuses that mean it's ALREADY processed for a role
        # This helps in skipping "Approve by Admin" or higher
        skip_words = ['APPROVED', 'COMPLETED', 'REJECTED', 'REVOKED']
        
        processed = 0
        success_count = 0
        fail_count = 0
        
        for i, smallcode in enumerate(smallcodes):
            task_progress[task_id]['progress'] = int((i / total) * 100)
            task_progress[task_id]['message'] = f'Processing {smallcode}...'
            
            assignments = api_client.get_assignments_by_smallcode(period_id, smallcode)
            
            if not assignments:
                continue
            
            task_progress[task_id]['total_assignments'] += len(assignments)
            
            for assign in assignments:
                assignment_id = assign['assignmentId']
                review_url = f'https://fasih-sm.bps.go.id/survey-collection/survey-review/{assignment_id}/{template_id}/{period_id}/a/1'
                
                try:
                    # Get current status
                    history = api_client.get_assignment_history(assignment_id)
                    status_list = parse_assignment_status(history)
                    current_status = status_list[-1]['status_assignment'] if status_list else 'Open'
                    
                    # Log message for debug
                    status_upper = current_status.upper()
                    
                    # Check if status allows action
                    if current_status not in allowed_statuses:
                        # Extra check: if it's already "APPROVED" or similar, we skip it clearly
                        is_already_processed = any(word in status_upper for word in skip_words)
                        reason = "already processed" if is_already_processed else f"status not eligible: {current_status}"
                        
                        log_data.append({
                            'assignment_id': assignment_id,
                            'smallcode': smallcode,
                            'status': current_status,
                            'action': action_type,
                            'result': 'skipped',
                            'message': f'Skipped ({reason})'
                        })
                        task_progress[task_id]['skip_count'] += 1
                        continue

                    # Special condition from original script: status_keberadaan check for revoke/reject
                    if action_type in ['revoke', 'reject']:
                        detail = api_client.get_assignment_detail(assignment_id)
                        status_keberadaan = get_status_keberadaan(detail)
                        # Original script specifically checks for '3. Tidak Ditemukan' for revoke/reject by Pengawas
                        if role == 'Pengawas' and status_keberadaan != '3. Tidak Ditemukan':
                            log_data.append({
                                'assignment_id': assignment_id,
                                'smallcode': smallcode,
                                'status': current_status,
                                'action': action_type,
                                'result': 'skipped',
                                'message': f'Skipped (status_keberadaan: {status_keberadaan})'
                            })
                            task_progress[task_id]['skip_count'] += 1
                            continue
                    
                    # Perform action using Selenium
                    result = selenium_manager.navigate_and_click(review_url, button_id)
                    
                    if result['success']:
                        success_count += 1
                        task_progress[task_id]['success_count'] = success_count
                        log_data.append({
                            'assignment_id': assignment_id,
                            'smallcode': smallcode,
                            'status': current_status,
                            'action': action_type,
                            'result': 'success',
                            'message': result['message']
                        })
                        task_progress[task_id]['logs'].append(f'✅ {assignment_id}: {action_type} success')
                    else:
                        fail_count += 1
                        task_progress[task_id]['fail_count'] = fail_count
                        log_data.append({
                            'assignment_id': assignment_id,
                            'smallcode': smallcode,
                            'status': current_status,
                            'action': action_type,
                            'result': 'failed',
                            'message': result['message']
                        })
                        task_progress[task_id]['logs'].append(f'❌ {assignment_id}: {result["message"]}')
                    
                    processed += 1
                    
                except Exception as e:
                    fail_count += 1
                    task_progress[task_id]['fail_count'] = fail_count
                    log_data.append({
                        'assignment_id': assignment_id,
                        'smallcode': smallcode,
                        'status': 'ERROR',
                        'action': action_type,
                        'result': 'error',
                        'message': str(e)
                    })
        
        # Save log to Excel
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"Log_{action_type.title()}_{kab_name}_{survey_name}_{period_name}_{timestamp}.xlsx"
        filepath = os.path.join(Config.LOG_DIR, filename)
        
        if log_data:
            df = pd.DataFrame(log_data)
            df.to_excel(filepath, index=False)
        
        task_progress[task_id]['status'] = 'completed'
        task_progress[task_id]['progress'] = 100
        task_progress[task_id]['message'] = f'Done! Success: {success_count}, Failed: {fail_count}'
        task_progress[task_id]['filename'] = filename
        task_progress[task_id]['logs'].append(f'📁 Log saved: {filename}')
        
        # Save session after action
        sess_data = selenium_manager.get_session_data()
        if sess_data['is_logged_in'] and sess_data['username']:
            session_manager.save_session(
                username=sess_data['username'],
                password=sess_data['password'],
                cookies=sess_data['cookies'],
                headers=sess_data['headers']
            )
            task_progress[task_id]['logs'].append('✅ Session updated')
        
    except Exception as e:
        task_progress[task_id]['status'] = 'error'
        task_progress[task_id]['message'] = str(e)
        task_progress[task_id]['logs'].append(f'❌ Error: {str(e)}')


@action_bp.route('/download-raw', methods=['POST'])
def download_raw():
    """Start raw data download task"""
    data = request.get_json()
    
    required = ['surveyId', 'periodId', 'templateId', 'groupId', 'kabId', 'kabName', 'surveyName', 'periodName']
    for field in required:
        if field not in data:
            return jsonify({'success': False, 'message': f'{field} required'}), 400
    
    task_id = datetime.now().strftime("%Y%m%d%H%M%S")
    
    # Store selected columns for filtering (optional)
    selected_columns = data.get('selectedColumns', [])
    task_progress[task_id] = {'selected_columns': selected_columns}
    
    # Start background thread
    thread = threading.Thread(
        target=download_raw_data_task,
        args=(
            task_id,
            data['surveyId'],
            data['periodId'],
            data['templateId'],
            data['groupId'],
            data['kabId'],
            data['kabName'],
            data['surveyName'],
            data['periodName']
        )
    )
    thread.start()
    
    return jsonify({'success': True, 'taskId': task_id})


@action_bp.route('/approve', methods=['POST'])
def approve():
    """Start approve task"""
    return _start_action_task('approve')


@action_bp.route('/revoke', methods=['POST'])
def revoke():
    """Start revoke task"""
    return _start_action_task('revoke')


@action_bp.route('/reject', methods=['POST'])
def reject():
    """Start reject task"""
    return _start_action_task('reject')


def _start_action_task(action_type: str):
    """Helper to start action tasks"""
    data = request.get_json()
    
    required = ['surveyId', 'periodId', 'templateId', 'groupId', 'kabId', 'kabName', 'surveyName', 'periodName']
    for field in required:
        if field not in data:
            return jsonify({'success': False, 'message': f'{field} required'}), 400
    
    task_id = datetime.now().strftime("%Y%m%d%H%M%S")
    
    thread = threading.Thread(
        target=approve_task,
        args=(
            task_id,
            data['surveyId'],
            data['periodId'],
            data['templateId'],
            data['groupId'],
            data['kabId'],
            data['kabName'],
            data['surveyName'],
            data['periodName'],
            action_type
        )
    )
    thread.start()
    
    return jsonify({'success': True, 'taskId': task_id})


@action_bp.route('/progress/<task_id>', methods=['GET'])
def get_progress(task_id):
    """Get task progress"""
    if task_id not in task_progress:
        return jsonify({'success': False, 'message': 'Task not found'}), 404
    
    return jsonify({
        'success': True,
        'data': task_progress[task_id]
    })


@action_bp.route('/download-file/<filename>', methods=['GET'])
def download_file(filename):
    """Download generated file"""
    # Try raw_data first, then log
    filepath = os.path.join(Config.RAW_DATA_DIR, filename)
    if not os.path.exists(filepath):
        filepath = os.path.join(Config.LOG_DIR, filename)
        
    if not os.path.exists(filepath):
        return jsonify({'success': False, 'message': 'File not found'}), 404
    
    # Determine mimetype based on file extension
    if filename.endswith('.xlsx'):
        mimetype = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    elif filename.endswith('.xls'):
        mimetype = 'application/vnd.ms-excel'
    else:
        mimetype = 'application/octet-stream'
    
    return send_file(
        filepath, 
        as_attachment=True, 
        download_name=filename,
        mimetype=mimetype
    )


@action_bp.route('/get-columns', methods=['GET'])
def get_columns():
    """Get available columns from the most recent download file"""
    survey_name = request.args.get('surveyName', '')
    
    # Find the most recent Raw_Data file for this survey
    output_dir = Config.RAW_DATA_DIR
    matching_files = []
    
    if os.path.exists(output_dir):
        for f in os.listdir(output_dir):
            if f.startswith('Raw_Data') and f.endswith('.xlsx'):
                if survey_name and survey_name in f:
                    matching_files.append(f)
                elif not survey_name:
                    matching_files.append(f)
    
    if not matching_files:
        # Return default columns if no file exists
        return jsonify({
            'success': True,
            'columns': [
                'assignment_id', 'smallcode', 'status_assignment', 'link_preview'
            ],
            'fromFile': None
        })
    
    # Get the most recent file
    matching_files.sort(reverse=True)
    latest_file = matching_files[0]
    filepath = os.path.join(output_dir, latest_file)
    
    try:
        df = pd.read_excel(filepath, nrows=0)  # Only read headers
        columns = smart_sort_columns(list(df.columns))
        
        return jsonify({
            'success': True,
            'columns': columns,
            'fromFile': latest_file
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@action_bp.route('/get-file-columns/<filename>', methods=['GET'])
def get_file_columns(filename):
    """Get columns from a specific file"""
    # Try raw_data first, then log
    filepath = os.path.join(Config.RAW_DATA_DIR, filename)
    if not os.path.exists(filepath):
        filepath = os.path.join(Config.LOG_DIR, filename)
        
    if not os.path.exists(filepath):
        return jsonify({'success': False, 'message': 'File not found'}), 404
    
    try:
        df = pd.read_excel(filepath, nrows=0)  # Only read headers
        columns = smart_sort_columns(list(df.columns))
        
        return jsonify({
            'success': True,
            'columns': columns,
            'filename': filename
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@action_bp.route('/export-filtered/<filename>', methods=['POST'])
def export_filtered(filename):
    """Export existing file with only selected columns (no re-scraping)"""
    data = request.get_json()
    selected_columns = data.get('selectedColumns', [])
    
    if not selected_columns:
        return jsonify({'success': False, 'message': 'No columns selected'}), 400
    
    # Find original file
    filepath = os.path.join(Config.RAW_DATA_DIR, filename)
    if not os.path.exists(filepath):
        filepath = os.path.join(Config.LOG_DIR, filename)
        
    if not os.path.exists(filepath):
        return jsonify({'success': False, 'message': 'File not found'}), 404
    
    try:
        # Read original file
        df = pd.read_excel(filepath)
        
        # Filter to only selected columns that exist
        existing_cols = [c for c in selected_columns if c in df.columns]
        
        if not existing_cols:
            return jsonify({'success': False, 'message': 'No valid columns found'}), 400
        
        df_filtered = df[existing_cols]
        
        # Generate new filename with _filtered suffix
        base_name = os.path.splitext(filename)[0]
        timestamp = datetime.now().strftime("%H%M%S")
        new_filename = f"{base_name}_filtered_{timestamp}.xlsx"
        new_filepath = os.path.join(Config.RAW_DATA_DIR, new_filename)
        
        # Save filtered file
        df_filtered.to_excel(new_filepath, index=False)
        
        return jsonify({
            'success': True,
            'filename': new_filename,
            'columns_count': len(existing_cols),
            'rows_count': len(df_filtered)
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@action_bp.route('/history', methods=['GET'])
def get_history():
    """Get list of files in raw_data and log directories"""
    history = []
    
    # Check RAW_DATA_DIR
    if os.path.exists(Config.RAW_DATA_DIR):
        for f in os.listdir(Config.RAW_DATA_DIR):
            if f.endswith('.xlsx'):
                path = os.path.join(Config.RAW_DATA_DIR, f)
                stats = os.stat(path)
                history.append({
                    'filename': f,
                    'type': 'raw_data',
                    'timestamp': datetime.fromtimestamp(stats.st_mtime).isoformat(),
                    'size': stats.st_size
                })
                
    # Check LOG_DIR
    if os.path.exists(Config.LOG_DIR):
        for f in os.listdir(Config.LOG_DIR):
            if f.endswith('.xlsx'):
                path = os.path.join(Config.LOG_DIR, f)
                stats = os.stat(path)
                history.append({
                    'filename': f,
                    'type': 'log',
                    'timestamp': datetime.fromtimestamp(stats.st_mtime).isoformat(),
                    'size': stats.st_size
                })
                
    # Sort by timestamp decending
    history.sort(key=lambda x: x['timestamp'], reverse=True)
    
    return jsonify({
        'success': True,
        'history': history
    })

