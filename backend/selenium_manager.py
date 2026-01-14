import time
import urllib.parse
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, ElementClickInterceptedException, StaleElementReferenceException
from webdriver_manager.chrome import ChromeDriverManager
from requests.cookies import RequestsCookieJar
from config import Config


class SeleniumManager:
    """Manages Selenium WebDriver for SSO login and UI interactions"""
    
    def __init__(self):
        self.driver = None
        self.is_logged_in = False
        self.cookies = None
        self.headers = None
        self.username = None
        self.password = None
        
    def setup_driver(self):
        """Initialize Chrome driver (non-headless for login)"""
        if self.driver:
            return self.driver
            
        service = Service(ChromeDriverManager().install())
        chrome_options = Options()
        # NON-HEADLESS for login (required for SSO popup)
        chrome_options.add_argument("--log-level=3")
        chrome_options.add_argument("--disable-logging")
        chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
        
        self.driver = webdriver.Chrome(service=service, options=chrome_options)
        return self.driver
    
    def minimize_driver(self):
        """Minimize browser window after successful login"""
        if self.driver:
            self.driver.minimize_window()
            
    def restore_driver(self):
        """Restore browser window when needed for UI actions"""
        if self.driver:
            self.driver.set_window_position(0, 0)
            
    def close_driver(self):
        """Close browser and cleanup"""
        if self.driver:
            try:
                self.driver.quit()
            except:
                pass
            self.driver = None
            self.is_logged_in = False
            self.cookies = None
    
    def inject_saved_session(self, session_data: dict) -> dict:
        """
        Inject saved session cookies into webdriver and validate
        Returns: {'success': bool, 'message': str}
        """
        try:
            self.setup_driver()
            
            cookies = session_data.get('cookies', [])
            if not cookies:
                return {'success': False, 'message': 'No cookies found in session data'}

            # Organize cookies by domain
            domain_cookies = {}
            for cookie in cookies:
                dom = cookie.get('domain', '.bps.go.id')
                if dom not in domain_cookies:
                    domain_cookies[dom] = []
                domain_cookies[dom].append(cookie)

            # Visit each major domain to set cookies
            # Start with SSO if present
            sso_domains = [d for d in domain_cookies.keys() if 'sso.bps.go.id' in d]
            if sso_domains:
                self.driver.get(Config.SSO_URL)
                time.sleep(1)
                for dom in sso_domains:
                    for cookie in domain_cookies[dom]:
                        try:
                            self.driver.add_cookie({
                                'name': cookie['name'],
                                'value': cookie['value'],
                                'domain': cookie.get('domain'),
                                'path': cookie.get('path', '/'),
                                'secure': cookie.get('secure', True)
                            })
                        except: pass

            # Then visit FASIH
            self.driver.get("https://fasih-sm.bps.go.id")
            time.sleep(1)
            fasih_domains = [d for d in domain_cookies.keys() if 'fasih' in d or d == '.bps.go.id' or d == 'bps.go.id']
            for dom in fasih_domains:
                for cookie in domain_cookies[dom]:
                    try:
                        self.driver.add_cookie({
                            'name': cookie['name'],
                            'value': cookie['value'],
                            'domain': cookie.get('domain'),
                            'path': cookie.get('path', '/'),
                            'secure': cookie.get('secure', True)
                        })
                    except: pass
            
            # Navigate to survey page to validate session
            self.driver.get(Config.FASIH_SURVEY_URL)
            time.sleep(4)
            
            # Check if we're logged in by looking for survey elements or redirect to login
            current_url = self.driver.current_url
            
            if 'sso.bps.go.id' in current_url or 'login' in current_url.lower():
                # Session invalid, redirected to login
                # Don't close driver yet, maybe keep it for manual login fallback?
                # Actually for restore feature, we should close it if it fails
                self.close_driver()
                return {'success': False, 'message': 'Session expired, redirected to login'}
            
            # Session valid, extract fresh cookies
            self.cookies = self._get_authenticated_cookies()
            self.headers = self._build_headers()
            self.username = session_data.get('username')
            self.password = session_data.get('password')
            self.is_logged_in = True
            
            # Minimize browser
            self.minimize_driver()
            
            return {'success': True, 'message': 'Session injected successfully'}
            
        except Exception as e:
            return {'success': False, 'message': str(e)}
    
    def login_sso(self, username: str, password: str) -> dict:
        """
        Login to SSO BPS
        Returns: {'success': bool, 'needs_otp': bool, 'message': str}
        """
        try:
            self.username = username
            self.password = password
            
            self.setup_driver()
            self.driver.get(Config.SSO_URL)
            time.sleep(2)
            
            # Fill login form
            self.driver.find_element(By.NAME, "username").send_keys(username)
            self.driver.find_element(By.NAME, "password").send_keys(password)
            self.driver.find_element(By.XPATH, '//*[@id="kc-login"]').click()
            time.sleep(2)
            
            # Check if OTP is required
            try:
                otp_element = self.driver.find_element(By.XPATH, '//*[@id="otp"]')
                return {'success': False, 'needs_otp': True, 'message': 'OTP required'}
            except:
                # No OTP required, continue to FASIH
                return self._complete_fasih_login()
                
        except Exception as e:
            return {'success': False, 'needs_otp': False, 'message': str(e)}
    
    def submit_otp(self, otp: str) -> dict:
        """Submit OTP and complete login with verification"""
        try:
            otp_element = self.driver.find_element(By.XPATH, '//*[@id="otp"]')
            
            # Clear any existing value first
            otp_element.clear()
            time.sleep(0.3)
            
            # Send OTP
            otp_element.send_keys(otp)
            time.sleep(0.5)
            
            # Verify the input value
            actual_value = otp_element.get_attribute('value')
            
            if actual_value != otp:
                # OTP input was blocked (probably by a notification)
                return {
                    'success': False,
                    'needs_otp': True,
                    'blocked': True,
                    'message': 'Input OTP terblokir. Tutup notifikasi password di browser, lalu klik Retry.'
                }
            
            # Click submit
            self.driver.find_element(By.XPATH, '//*[@id="kc-login"]').click()
            time.sleep(2)
            
            # Check if still on OTP page (wrong OTP)
            try:
                self.driver.find_element(By.XPATH, '//*[@id="otp"]')
                return {
                    'success': False,
                    'needs_otp': True,
                    'blocked': False,
                    'message': 'OTP salah. Silakan coba lagi.'
                }
            except:
                # OTP accepted, continue to FASIH
                return self._complete_fasih_login()
            
        except Exception as e:
            return {'success': False, 'needs_otp': False, 'blocked': False, 'message': str(e)}
    
    def clear_otp_field(self) -> dict:
        """Clear OTP field for retry"""
        try:
            otp_element = self.driver.find_element(By.XPATH, '//*[@id="otp"]')
            otp_element.clear()
            return {'success': True, 'message': 'OTP field cleared'}
        except Exception as e:
            return {'success': False, 'message': str(e)}
    
    def _complete_fasih_login(self) -> dict:
        """Complete login to FASIH-SM after SSO"""
        try:
            # Navigate to FASIH OAuth
            self.driver.get(Config.FASIH_OAUTH_URL)
            time.sleep(5)
            
            # Navigate to survey page to get cookies
            self.driver.get(Config.FASIH_SURVEY_URL)
            time.sleep(3)
            
            # Get and store cookies
            self.cookies = self._get_authenticated_cookies()
            self.headers = self._build_headers()
            self.is_logged_in = True
            
            # Minimize after successful login
            self.minimize_driver()
            
            return {'success': True, 'needs_otp': False, 'message': 'Login successful'}
            
        except Exception as e:
            return {'success': False, 'needs_otp': False, 'message': str(e)}
    
    def _get_authenticated_cookies(self) -> RequestsCookieJar:
        """Extract cookies from Selenium driver"""
        selenium_cookies = self.driver.get_cookies()
        jar = RequestsCookieJar()
        for cookie in selenium_cookies:
            jar.set(
                name=cookie['name'],
                value=cookie['value'],
                domain=cookie.get('domain'),
                path=cookie.get('path', '/'),
                secure=cookie.get('secure', False)
            )
        return jar
    
    def _build_headers(self) -> dict:
        """Build headers with XSRF token"""
        xsrf_token = ''
        if self.cookies:
            xsrf_token = urllib.parse.unquote(self.cookies.get('XSRF-TOKEN', ''))
        
        return {
            'X-Requested-With': 'XMLHttpRequest',
            'X-XSRF-TOKEN': xsrf_token,
            'Referer': 'https://fasih-sm.bps.go.id/',
            'User-Agent': 'Mozilla/5.0',
            'Content-Type': 'application/json',
            'Accept': 'application/json, text/plain, */*',
            'Origin': 'https://fasih-sm.bps.go.id'
        }
        
    def get_session_data(self) -> dict:
        """Get current session data for API requests"""
        return {
            'cookies': self.cookies,
            'headers': self.headers,
            'is_logged_in': self.is_logged_in,
            'username': self.username,
            'password': self.password
        }
    
    def navigate_and_click(self, url: str, button_id: str, max_attempts: int = 5) -> dict:
        """
        Navigate to URL and click a button (for approve/reject/revoke)
        Returns: {'success': bool, 'message': str}
        """
        try:
            self.driver.get(url)
            wait = WebDriverWait(self.driver, 30)
            
            # Wait for button to be present and clickable
            wait.until(EC.presence_of_element_located((By.ID, button_id)))
            button = wait.until(EC.element_to_be_clickable((By.ID, button_id)))
            
            # Try to click with retry
            clicked = False
            attempt = 0
            
            while not clicked and attempt < max_attempts:
                try:
                    time.sleep(0.5)
                    button.click()
                    clicked = True
                except (ElementClickInterceptedException, StaleElementReferenceException):
                    attempt += 1
                    button = wait.until(EC.element_to_be_clickable((By.ID, button_id)))
                except Exception as e:
                    return {'success': False, 'message': str(e)}
            
            if not clicked:
                return {'success': False, 'message': f'Failed to click {button_id} after {max_attempts} attempts'}
            
            # Handle confirmation dialogs
            try:
                confirm_xpath = '//*[@id="fasih"]/div/div/div[6]/button[1]'
                wait.until(EC.presence_of_element_located((By.XPATH, confirm_xpath)))
                wait.until(EC.element_to_be_clickable((By.XPATH, confirm_xpath)))
                confirm1 = self.driver.find_element(By.XPATH, confirm_xpath)
                confirm1.click()
                
                # Second confirmation if exists
                try:
                    time.sleep(0.5)
                    wait.until(EC.element_to_be_clickable((By.XPATH, confirm_xpath)))
                    confirm2 = self.driver.find_element(By.XPATH, confirm_xpath)
                    confirm2.click()
                except TimeoutException:
                    pass
                    
            except TimeoutException:
                pass
            
            return {'success': True, 'message': f'{button_id} clicked successfully'}
            
        except TimeoutException:
            return {'success': False, 'message': 'Timeout waiting for element'}
        except Exception as e:
            return {'success': False, 'message': str(e)}


# Global instance
selenium_manager = SeleniumManager()
