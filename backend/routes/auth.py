from flask import Blueprint, request, jsonify
from selenium_manager import selenium_manager
from session_manager import session_manager

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/check-credentials', methods=['POST'])
def check_credentials():
    """
    Check if there's a saved session file for username (only get password, no validation)
    Body: { "username": str }
    Returns: { "has_session": bool, "password": str }
    """
    data = request.get_json()
    username = data.get('username', '')
    
    if not username:
        return jsonify({'has_session': False, 'password': ''})
    
    # Only check for saved credentials, don't validate
    creds = session_manager.check_saved_credentials(username)
    
    return jsonify({
        'has_session': creds['exists'],
        'password': creds.get('password', '')
    })


@auth_bp.route('/login', methods=['POST'])
def login():
    """
    Start SSO login process (with session injection attempt)
    Body: { "username": str, "password": str }
    """
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    if not username or not password:
        return jsonify({'success': False, 'message': 'Username and password required'}), 400
    
    # Try to inject saved session first
    session_data = session_manager.load_session(username)
    
    if session_data:
        # Setup webdriver and inject session
        inject_result = selenium_manager.inject_saved_session(session_data)
        
        if inject_result.get('success'):
            # Session injected and valid
            session_manager.set_logged_in(
                cookies=selenium_manager.cookies,
                headers=selenium_manager.headers,
                username=username
            )
            
            # Refresh session file with fresh cookies/headers
            session_manager.save_session(
                username=username,
                password=password,
                cookies=selenium_manager.cookies,
                headers=selenium_manager.headers
            )
            
            return jsonify({
                'success': True,
                'needs_otp': False,
                'message': 'Session restored successfully',
                'restored': True
            })
    
    # Session not found or invalid, proceed with normal SSO login
    result = selenium_manager.login_sso(username, password)
    
    # If login successful, save session
    if result.get('success'):
        sess_data = selenium_manager.get_session_data()
        session_manager.save_session(
            username=username,
            password=password,
            cookies=sess_data['cookies'],
            headers=sess_data['headers']
        )
    
    return jsonify(result)


@auth_bp.route('/submit-otp', methods=['POST'])
def submit_otp():
    """
    Submit OTP for login
    Body: { "otp": str }
    """
    data = request.get_json()
    otp = data.get('otp')
    
    if not otp:
        return jsonify({'success': False, 'message': 'OTP required'}), 400
    
    result = selenium_manager.submit_otp(otp)
    
    # If login successful, save session
    if result.get('success'):
        sess_data = selenium_manager.get_session_data()
        session_manager.save_session(
            username=sess_data['username'],
            password=sess_data['password'],
            cookies=sess_data['cookies'],
            headers=sess_data['headers']
        )
    
    return jsonify(result)


@auth_bp.route('/clear-otp', methods=['POST'])
def clear_otp():
    """Clear OTP field for retry"""
    result = selenium_manager.clear_otp_field()
    return jsonify(result)


@auth_bp.route('/status', methods=['GET'])
def status():
    """Check login status"""
    # First check session_manager
    if session_manager.is_logged_in:
        return jsonify({'is_logged_in': True})
    
    # Then check selenium_manager
    sess_data = selenium_manager.get_session_data()
    return jsonify({
        'is_logged_in': sess_data['is_logged_in']
    })


@auth_bp.route('/logout', methods=['POST'])
def logout():
    """Logout and close browser"""
    selenium_manager.close_driver()
    session_manager.clear()
    return jsonify({'success': True, 'message': 'Logged out'})
