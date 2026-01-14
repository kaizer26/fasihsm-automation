from flask import Blueprint, request, jsonify
from api_client import api_client

region_bp = Blueprint('region', __name__)


@region_bp.route('/metadata/<group_id>', methods=['GET'])
def get_metadata(group_id):
    """Get region metadata including levels"""
    try:
        data = api_client.get_region_metadata(group_id)
        return jsonify({
            'success': True,
            'data': data.get('data', {})
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@region_bp.route('/provinsi', methods=['GET'])
def get_provinsi():
    """Get list of provinces"""
    group_id = request.args.get('groupId')
    if not group_id:
        return jsonify({'success': False, 'message': 'groupId required'}), 400
    
    try:
        data = api_client.get_provinsi(group_id)
        return jsonify({
            'success': True,
            'data': [{
                'id': p['id'],
                'name': p['name'],
                'code': p['code'],
                'fullCode': p['fullCode']
            } for p in data]
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@region_bp.route('/kabupaten', methods=['GET'])
def get_kabupaten():
    """Get list of kabupaten/kota"""
    group_id = request.args.get('groupId')
    prov_fullcode = request.args.get('provFullCode')
    
    if not group_id or not prov_fullcode:
        return jsonify({'success': False, 'message': 'groupId and provFullCode required'}), 400
    
    try:
        data = api_client.get_kabupaten(group_id, prov_fullcode)
        return jsonify({
            'success': True,
            'data': [{
                'id': k['id'],
                'name': k['name'],
                'code': k['code'],
                'fullCode': k['fullCode']
            } for k in data]
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@region_bp.route('/kecamatan', methods=['GET'])
def get_kecamatan():
    """Get list of kecamatan"""
    group_id = request.args.get('groupId')
    kab_id = request.args.get('kabId')
    
    if not group_id or not kab_id:
        return jsonify({'success': False, 'message': 'groupId and kabId required'}), 400
    
    try:
        data = api_client.get_kecamatan(group_id, kab_id)
        return jsonify({
            'success': True,
            'data': [{
                'id': k['id'],
                'name': k['name'],
                'code': k['code'],
                'fullCode': k['fullCode']
            } for k in data]
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@region_bp.route('/desa', methods=['GET'])
def get_desa():
    """Get list of desa/kelurahan"""
    group_id = request.args.get('groupId')
    kec_id = request.args.get('kecId')
    
    if not group_id or not kec_id:
        return jsonify({'success': False, 'message': 'groupId and kecId required'}), 400
    
    try:
        data = api_client.get_desa(group_id, kec_id)
        return jsonify({
            'success': True,
            'data': [{
                'id': d['id'],
                'name': d['name'],
                'code': d['code'],
                'fullCode': d['fullCode']
            } for d in data]
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@region_bp.route('/sls', methods=['GET'])
def get_sls():
    """Get list of SLS"""
    group_id = request.args.get('groupId')
    desa_id = request.args.get('desaId')
    
    if not group_id or not desa_id:
        return jsonify({'success': False, 'message': 'groupId and desaId required'}), 400
    
    try:
        data = api_client.get_sls(group_id, desa_id)
        return jsonify({
            'success': True,
            'data': [{
                'id': s['id'],
                'name': s['name'],
                'code': s['code'],
                'fullCode': s['fullCode']
            } for s in data]
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500
