import json
from session_manager import session_manager
from config import Config


class APIClient:
    """Client for FASIH-SM API calls"""
    
    def __init__(self):
        pass
    
    def _get_session(self):
        """Get valid session or raise error"""
        session = session_manager.get_session()
        if not session:
            raise Exception("Not logged in")
        return session
    
    # ============ SURVEY APIs ============
    
    def get_surveys(self, survey_type: str = "Pencacahan", page_size: int = 100) -> dict:
        """Get list of surveys"""
        session = self._get_session()
        url = f'{Config.SURVEY_API}/surveys/datatable?surveyType={survey_type}'
        payload = {
            "pageNumber": 0,
            "pageSize": page_size,
            "sortBy": "CREATED_AT",
            "sortDirection": "DESC",
            "keywordSearch": ""
        }
        resp = session.post(url, json=payload)
        resp.raise_for_status()
        return resp.json()
    
    def get_survey_detail(self, survey_id: str) -> dict:
        """Get survey detail including periods"""
        session = self._get_session()
        url = f'{Config.SURVEY_API}/surveys/{survey_id}'
        resp = session.get(url)
        resp.raise_for_status()
        return resp.json()
    
    def get_user_role(self, survey_period_id: str) -> str:
        """Get user role for a survey period"""
        session = self._get_session()
        url = f'{Config.SURVEY_API}/users/myinfo?surveyPeriodId={survey_period_id}'
        resp = session.get(url)
        resp.raise_for_status()
        return resp.json()['data']['surveyRole']['description']
    
    # ============ REGION APIs ============
    
    def get_region_metadata(self, group_id: str) -> dict:
        """Get region metadata including levels"""
        session = self._get_session()
        url = f'{Config.REGION_API}/region-metadata?id={group_id}'
        resp = session.get(url)
        resp.raise_for_status()
        return resp.json()
    
    def get_provinsi(self, group_id: str) -> list:
        """Get list of provinces"""
        session = self._get_session()
        url = f'{Config.REGION_API}/region/level1?groupId={group_id}'
        resp = session.get(url)
        resp.raise_for_status()
        return resp.json().get('data', [])
    
    def get_kabupaten(self, group_id: str, prov_fullcode: str) -> list:
        """Get list of kabupaten/kota"""
        session = self._get_session()
        url = f'{Config.REGION_API}/region/level2?groupId={group_id}&level1FullCode={prov_fullcode}'
        resp = session.get(url)
        resp.raise_for_status()
        return resp.json().get('data', [])
    
    def get_kecamatan(self, group_id: str, kab_id: str) -> list:
        """Get list of kecamatan"""
        session = self._get_session()
        url = f'{Config.REGION_API}/region/level3?groupId={group_id}&level2Id={kab_id}'
        resp = session.get(url)
        resp.raise_for_status()
        return resp.json().get('data', [])
    
    def get_desa(self, group_id: str, kec_id: str) -> list:
        """Get list of desa/kelurahan"""
        session = self._get_session()
        url = f'{Config.REGION_API}/region/level4?groupId={group_id}&level3Id={kec_id}'
        resp = session.get(url)
        resp.raise_for_status()
        return resp.json().get('data', [])
    
    def get_sls(self, group_id: str, desa_id: str) -> list:
        """Get list of SLS"""
        session = self._get_session()
        url = f'{Config.REGION_API}/region/level5?groupId={group_id}&level4Id={desa_id}'
        resp = session.get(url)
        resp.raise_for_status()
        return resp.json().get('data', [])
    
    def get_subsls(self, group_id: str, sls_id: str) -> list:
        """Get list of Sub SLS"""
        session = self._get_session()
        url = f'{Config.REGION_API}/region/level6?groupId={group_id}&level5Id={sls_id}'
        resp = session.get(url)
        resp.raise_for_status()
        return resp.json().get('data', [])
    
    # ============ ASSIGNMENT APIs ============
    
    def get_assignments_by_smallcode(self, survey_period_id: str, smallcode: str) -> list:
        """Get assignments for a specific smallcode"""
        session = self._get_session()
        url = f'{Config.ASSIGNMENT_API}/assignments/get-principal-values-by-smallest-code/{survey_period_id}/{smallcode}'
        resp = session.get(url)
        if resp.status_code != 200 or not resp.text.strip():
            return []
        return resp.json().get('data', [])
    
    def get_assignment_detail(self, assignment_id: str) -> dict:
        """Get detailed assignment data with answers"""
        session = self._get_session()
        url = f'{Config.ASSIGNMENT_API}/assignment/get-by-id-with-data-for-scm?id={assignment_id}'
        resp = session.get(url)
        resp.raise_for_status()
        return resp.json()
    
    def get_assignment_history(self, assignment_id: str) -> dict:
        """Get assignment status history"""
        session = self._get_session()
        url = f'{Config.ASSIGNMENT_API}/assignment-history/get-by-assignment-id?assignmentId={assignment_id}'
        resp = session.get(url)
        resp.raise_for_status()
        return resp.json()


# Global instance
api_client = APIClient()
