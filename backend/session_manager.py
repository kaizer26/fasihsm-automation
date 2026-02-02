import os
import json
import requests
from datetime import datetime
from requests.cookies import RequestsCookieJar
from config import Config


class SessionManager:
    """Manages API session with cookies and headers, with file persistence"""
    
    def __init__(self):
        self.session = None
        self.cookies = None
        self.headers = None
        self.username = None
        self.is_logged_in = False
        
    def _get_session_filepath(self, username: str) -> str:
        """Get session file path for a username"""
        # Lowercase and clean username
        if not username:
            return ""
            
        clean_username = username.lower().strip()
        if '@' in clean_username:
            clean_username = clean_username.split('@')[0]
            
        filename = f"session_{clean_username}.json"
        # Ensure directory exists
        os.makedirs(Config.SESSION_DIR, exist_ok=True)
        return os.path.join(Config.SESSION_DIR, filename)
    
    def save_session(self, username: str, password: str, cookies: RequestsCookieJar, headers: dict):
        """Save session to file"""
        filepath = self._get_session_filepath(username)
        
        # Convert cookies to serializable format
        cookies_list = []
        for cookie in cookies:
            cookies_list.append({
                'name': cookie.name,
                'value': cookie.value,
                'domain': cookie.domain,
                'path': cookie.path,
                'secure': cookie.secure
            })
        
        session_data = {
            'username': username,
            'password': password,
            'cookies': cookies_list,
            'headers': headers,
            'saved_at': datetime.now().isoformat()
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(session_data, f, ensure_ascii=False, indent=2)
        
        # Update internal state
        self.cookies = cookies
        self.headers = headers
        self.username = username
        self.is_logged_in = True
        
        return True
    
    def load_session(self, username: str) -> dict:
        """Load session from file, returns None if not found"""
        filepath = self._get_session_filepath(username)
        print(f"      Looking for session file: {filepath}")
        
        if not os.path.exists(filepath):
            print(f"      File not found: {filepath}")
            return None
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return data
        except:
            return None
    
    def check_saved_credentials(self, username: str) -> dict:
        """Check if there are saved credentials for a username"""
        session_data = self.load_session(username)
        if session_data:
            return {
                'exists': True,
                'password': session_data.get('password', ''),
                'saved_at': session_data.get('saved_at', '')
            }
        return {'exists': False, 'password': '', 'saved_at': ''}
    
    def inject_session(self, username: str) -> bool:
        """Inject saved session into requests session"""
        session_data = self.load_session(username)
        if not session_data:
            return False
        
        try:
            # Recreate cookies jar
            jar = RequestsCookieJar()
            for cookie in session_data.get('cookies', []):
                jar.set(
                    name=cookie['name'],
                    value=cookie['value'],
                    domain=cookie.get('domain'),
                    path=cookie.get('path', '/'),
                    secure=cookie.get('secure', False)
                )
            
            self.cookies = jar
            self.headers = session_data.get('headers', {})
            self.username = username
            
            return True
        except:
            return False
    
    def validate_session(self) -> bool:
        """Test if current session is valid by trying to fetch surveys"""
        if not self.cookies or not self.headers:
            return False
        
        try:
            session = requests.Session()
            session.cookies = self.cookies
            session.headers.update(self.headers)
            
            resp = session.get(
                "https://fasih-sm.bps.go.id/survey/api/v1/surveys",
                allow_redirects=False,
                timeout=10
            )
            
            if resp.status_code == 200:
                self.session = session
                self.is_logged_in = True
                return True
            return False
        except:
            return False
    
    def get_session(self) -> requests.Session:
        """Get or create requests session with current cookies"""
        if not self.is_logged_in or not self.cookies:
            return None
            
        if self.session is None:
            self.session = requests.Session()
            
        self.session.cookies = self.cookies
        self.session.headers.update(self.headers)
        
        return self.session
    
    def get_session_data(self) -> dict:
        """Get current session data"""
        return {
            'cookies': self.cookies,
            'headers': self.headers,
            'is_logged_in': self.is_logged_in,
            'username': self.username
        }
    
    def set_logged_in(self, cookies: RequestsCookieJar, headers: dict, username: str):
        """Set session as logged in with cookies and headers"""
        self.cookies = cookies
        self.headers = headers
        self.username = username
        self.is_logged_in = True
    
    def clear(self):
        """Clear session"""
        self.session = None
        self.cookies = None
        self.headers = None
        self.username = None
        self.is_logged_in = False


# Global instance
session_manager = SessionManager()
