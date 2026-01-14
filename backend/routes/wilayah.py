import os
import json
from flask import Blueprint, request, jsonify
from api_client import api_client
from config import Config

wilayah_bp = Blueprint('wilayah', __name__)


def get_wilayah_filepath(survey_id: str, period_id: str, kab_id: str) -> str:
    """Generate filepath for wilayah cache file"""
    filename = f"wilayah_{survey_id}_{period_id}_{kab_id}.json"
    os.makedirs(Config.WILAYAH_DIR, exist_ok=True)
    return os.path.join(Config.WILAYAH_DIR, filename)


def get_all_smallcodes_with_details(group_id: str, kab_id: str) -> list:
    """Get all smallcodes with full details for a kabupaten"""
    result = []
    
    # Get region metadata for levels
    metadata = api_client.get_region_metadata(group_id)
    level_region = metadata.get('data', {}).get('level', [])
    
    kecamatan_list = api_client.get_kecamatan(group_id, kab_id)
    
    for kec in kecamatan_list:
        if len(level_region) == 3:
            result.append({
                'smallcode': kec['fullCode'],
                'kecamatan': kec['name'],
                'desa': None,
                'sls': None
            })
            continue
            
        desa_list = api_client.get_desa(group_id, kec['id'])
        
        for desa in desa_list:
            if len(level_region) == 4:
                result.append({
                    'smallcode': desa['fullCode'],
                    'kecamatan': kec['name'],
                    'desa': desa['name'],
                    'sls': None
                })
                continue
                
            sls_list = api_client.get_sls(group_id, desa['id'])
            
            for sls in sls_list:
                if len(level_region) == 5:
                    result.append({
                        'smallcode': sls['fullCode'],
                        'kecamatan': kec['name'],
                        'desa': desa['name'],
                        'sls': sls['name']
                    })
                    continue
                    
                subsls_list = api_client.get_subsls(group_id, sls['id'])
                for subsls in subsls_list:
                    result.append({
                        'smallcode': subsls['fullCode'],
                        'kecamatan': kec['name'],
                        'desa': desa['name'],
                        'sls': f"{sls['name']} / {subsls['name']}"
                    })
    
    return result


@wilayah_bp.route('/status', methods=['GET'])
def check_status():
    """Check if wilayah cache file exists"""
    survey_id = request.args.get('surveyId')
    period_id = request.args.get('periodId')
    kab_id = request.args.get('kabId')
    
    if not all([survey_id, period_id, kab_id]):
        return jsonify({'success': False, 'message': 'Missing parameters'}), 400
    
    filepath = get_wilayah_filepath(survey_id, period_id, kab_id)
    
    if os.path.exists(filepath):
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return jsonify({
            'success': True,
            'exists': True,
            'count': len(data.get('smallcodes', []))
        })
    
    return jsonify({
        'success': True,
        'exists': False,
        'count': 0
    })


@wilayah_bp.route('/fetch', methods=['POST'])
def fetch_wilayah():
    """Fetch wilayah from FASIH-SM API and save to cache"""
    data = request.get_json()
    
    survey_id = data.get('surveyId')
    period_id = data.get('periodId')
    kab_id = data.get('kabId')
    group_id = data.get('groupId')
    
    if not all([survey_id, period_id, kab_id, group_id]):
        return jsonify({'success': False, 'message': 'Missing parameters'}), 400
    
    try:
        # Fetch all smallcodes
        smallcodes = get_all_smallcodes_with_details(group_id, kab_id)
        
        # Save to file
        filepath = get_wilayah_filepath(survey_id, period_id, kab_id)
        cache_data = {
            'surveyId': survey_id,
            'periodId': period_id,
            'kabId': kab_id,
            'groupId': group_id,
            'smallcodes': smallcodes
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(cache_data, f, ensure_ascii=False, indent=2)
        
        return jsonify({
            'success': True,
            'count': len(smallcodes),
            'message': f'Fetched and cached {len(smallcodes)} smallcodes'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@wilayah_bp.route('/data', methods=['GET'])
def get_wilayah_data():
    """Get cached wilayah data"""
    survey_id = request.args.get('surveyId')
    period_id = request.args.get('periodId')
    kab_id = request.args.get('kabId')
    
    if not all([survey_id, period_id, kab_id]):
        return jsonify({'success': False, 'message': 'Missing parameters'}), 400
    
    filepath = get_wilayah_filepath(survey_id, period_id, kab_id)
    
    if not os.path.exists(filepath):
        return jsonify({'success': False, 'message': 'Cache not found'}), 404
    
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    return jsonify({
        'success': True,
        'data': data
    })
