import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'fasih-sm-secret-key-2026')
    SESSION_TYPE = 'filesystem'
    SESSION_PERMANENT = False
    SESSION_USE_SIGNER = True
    
    # FASIH-SM URLs
    SSO_URL = 'https://sso.bps.go.id'
    FASIH_BASE_URL = 'https://fasih-sm.bps.go.id'
    FASIH_OAUTH_URL = f'{FASIH_BASE_URL}/oauth2/authorization/ics'
    FASIH_SURVEY_URL = f'{FASIH_BASE_URL}/survey-collection/survey'
    
    # API Endpoints
    SURVEY_API = f'{FASIH_BASE_URL}/survey/api/v1'
    REGION_API = f'{FASIH_BASE_URL}/region/api/v1'
    ASSIGNMENT_API = f'{FASIH_BASE_URL}/assignment-general/api'
    
    # Output directories - organized by category
    OUTPUT_DIR = os.path.join(os.path.dirname(__file__), 'output')
    SESSION_DIR = os.path.join(OUTPUT_DIR, 'session')
    WILAYAH_DIR = os.path.join(OUTPUT_DIR, 'wilayah')
    RAW_DATA_DIR = os.path.join(OUTPUT_DIR, 'raw_data')
    LOG_DIR = os.path.join(OUTPUT_DIR, 'log')
    
    @staticmethod
    def init_app(app):
        # Create all output directories
        os.makedirs(Config.OUTPUT_DIR, exist_ok=True)
        os.makedirs(Config.SESSION_DIR, exist_ok=True)
        os.makedirs(Config.WILAYAH_DIR, exist_ok=True)
        os.makedirs(Config.RAW_DATA_DIR, exist_ok=True)
        os.makedirs(Config.LOG_DIR, exist_ok=True)
