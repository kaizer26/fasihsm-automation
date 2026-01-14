from flask import Blueprint, jsonify
from api_client import api_client

survey_bp = Blueprint('survey', __name__)


@survey_bp.route('/', methods=['GET'])
def get_surveys():
    """Get list of surveys"""
    try:
        data = api_client.get_surveys()
        surveys = data.get('data', {}).get('content', [])
        return jsonify({
            'success': True,
            'data': [{
                'id': s['id'],
                'name': s['name'],
                'surveyType': s.get('surveyType', ''),
                'regionGroupId': s.get('regionGroupId', '')
            } for s in surveys]
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@survey_bp.route('/<survey_id>', methods=['GET'])
def get_survey_detail(survey_id):
    """Get survey detail with periods"""
    try:
        data = api_client.get_survey_detail(survey_id)
        survey_data = data.get('data', {})
        
        return jsonify({
            'success': True,
            'data': {
                'id': survey_data.get('id'),
                'name': survey_data.get('name'),
                'regionGroupId': survey_data.get('regionGroupId'),
                'templateId': survey_data.get('surveyTemplates', [{}])[-1].get('templateId') if survey_data.get('surveyTemplates') else None,
                'periods': [{
                    'id': p['id'],
                    'name': p['name'],
                    'startDate': p['startDate'],
                    'endDate': p['endDate']
                } for p in survey_data.get('surveyPeriods', [])]
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@survey_bp.route('/<survey_id>/role/<period_id>', methods=['GET'])
def get_user_role(survey_id, period_id):
    """Get user role for survey period"""
    try:
        role = api_client.get_user_role(period_id)
        return jsonify({
            'success': True,
            'data': {'role': role}
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500
