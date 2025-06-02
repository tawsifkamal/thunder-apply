"""Utility functions for web automation tasks."""

import time
import logging
from typing import Dict, List, Optional, Callable, Any
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium import webdriver

logger = logging.getLogger(__name__)


class RetryHandler:
    """Handle retry logic for automation tasks."""
    
    def __init__(self, max_retries: int = 3, delay: float = 2.0):
        self.max_retries = max_retries
        self.delay = delay
    
    def retry(self, func: Callable, *args, **kwargs) -> Any:
        """Retry a function with exponential backoff."""
        last_exception = None
        
        for attempt in range(self.max_retries):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                last_exception = e
                if attempt < self.max_retries - 1:
                    wait_time = self.delay * (2 ** attempt)
                    logger.warning(f"Attempt {attempt + 1} failed: {e}. Retrying in {wait_time}s...")
                    time.sleep(wait_time)
                else:
                    logger.error(f"All {self.max_retries} attempts failed")
        
        raise last_exception


class FormFieldMapper:
    """Map profile data to form fields using various strategies."""
    
    @staticmethod
    def create_mapping_by_labels(driver: webdriver.Chrome, profile: Dict) -> Dict:
        """Create field mapping by analyzing form labels."""
        mapping = {}
        
        # Common field mappings
        field_mappings = {
            'first_name': ['first name', 'firstname', 'fname', 'given name'],
            'last_name': ['last name', 'lastname', 'lname', 'surname', 'family name'],
            'email': ['email', 'email address', 'e-mail'],
            'phone_number': ['phone', 'phone number', 'telephone', 'mobile'],
            'location': ['location', 'address', 'city', 'location preference'],
        }
        
        try:
            # Find all input elements
            inputs = driver.find_elements(By.TAG_NAME, "input")
            
            for input_elem in inputs:
                # Get various attributes that might indicate field purpose
                field_id = input_elem.get_attribute("id")
                field_name = input_elem.get_attribute("name")
                field_placeholder = input_elem.get_attribute("placeholder")
                field_type = input_elem.get_attribute("type")
                
                # Try to find associated label
                label_text = FormFieldMapper._get_label_text(driver, input_elem)
                
                # Combine all text sources
                all_text = " ".join(filter(None, [
                    field_id, field_name, field_placeholder, label_text
                ])).lower()
                
                # Match against known patterns
                for profile_key, patterns in field_mappings.items():
                    if any(pattern in all_text for pattern in patterns):
                        mapping[profile_key] = {
                            "id": field_id,
                            "name": field_name,
                            "type": "file" if field_type == "file" else "input"
                        }
                        break
            
            logger.info(f"Created mapping for {len(mapping)} fields")
            return mapping
            
        except Exception as e:
            logger.error(f"Error creating field mapping: {e}")
            return {}
    
    @staticmethod
    def _get_label_text(driver: webdriver.Chrome, input_elem) -> str:
        """Get the label text associated with an input element."""
        try:
            # Try to find label by 'for' attribute
            field_id = input_elem.get_attribute("id")
            if field_id:
                label = driver.find_element(By.XPATH, f"//label[@for='{field_id}']")
                return label.text
        except NoSuchElementException:
            pass
        
        try:
            # Try to find parent label
            parent = input_elem.find_element(By.XPATH, "..")
            if parent.tag_name.lower() == "label":
                return parent.text
        except NoSuchElementException:
            pass
        
        return ""


class ElementInteractor:
    """Handle common element interaction patterns."""
    
    def __init__(self, driver: webdriver.Chrome, retry_handler: Optional[RetryHandler] = None):
        self.driver = driver
        self.retry_handler = retry_handler or RetryHandler()
    
    def safe_click(self, locator: tuple, timeout: int = 10) -> bool:
        """Safely click an element with retry logic."""
        def _click():
            element = WebDriverWait(self.driver, timeout).until(
                EC.element_to_be_clickable(locator)
            )
            self.driver.execute_script("arguments[0].scrollIntoView(true);", element)
            time.sleep(0.5)  # Brief pause after scrolling
            element.click()
            return True
        
        try:
            return self.retry_handler.retry(_click)
        except Exception as e:
            logger.error(f"Failed to click element {locator}: {e}")
            return False
    
    def safe_send_keys(self, locator: tuple, text: str, timeout: int = 10, clear_first: bool = True) -> bool:
        """Safely send keys to an element with retry logic."""
        def _send_keys():
            element = WebDriverWait(self.driver, timeout).until(
                EC.visibility_of_element_located(locator)
            )
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
            
            if clear_first:
                element.clear()
            
            element.send_keys(text)
            return True
        
        try:
            return self.retry_handler.retry(_send_keys)
        except Exception as e:
            logger.error(f"Failed to send keys to element {locator}: {e}")
            return False
    
    def wait_for_page_load(self, timeout: int = 30) -> bool:
        """Wait for page to fully load."""
        try:
            WebDriverWait(self.driver, timeout).until(
                lambda driver: driver.execute_script("return document.readyState") == "complete"
            )
            return True
        except TimeoutException:
            logger.warning("Page load timeout")
            return False


class JobApplicationHelper:
    """Helper functions specific to job application automation."""
    
    @staticmethod
    def detect_application_form(driver: webdriver.Chrome) -> bool:
        """Detect if current page contains a job application form."""
        form_indicators = [
            "//form[contains(@class, 'application')]",
            "//form[contains(@id, 'application')]",
            "//input[@type='file']",  # Resume upload
            "//input[contains(@name, 'resume')]",
            "//button[contains(text(), 'Apply')]",
            "//button[contains(text(), 'Submit Application')]"
        ]
        
        for indicator in form_indicators:
            try:
                driver.find_element(By.XPATH, indicator)
                return True
            except NoSuchElementException:
                continue
        
        return False
    
    @staticmethod
    def find_apply_button(driver: webdriver.Chrome) -> Optional[tuple]:
        """Find the apply button on the page."""
        button_selectors = [
            (By.XPATH, "//button[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'apply')]"),
            (By.XPATH, "//a[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'apply')]"),
            (By.XPATH, "//input[@type='submit' and contains(translate(@value, 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'apply')]"),
        ]
        
        for selector in button_selectors:
            try:
                driver.find_element(*selector)
                return selector
            except NoSuchElementException:
                continue
        
        return None
    
    @staticmethod
    def extract_job_details(driver: webdriver.Chrome) -> Dict[str, str]:
        """Extract job details from the current page."""
        details = {}
        
        # Common selectors for job details
        selectors = {
            'title': [
                "//h1[contains(@class, 'job-title')]",
                "//h1[contains(@class, 'title')]",
                "//h1",
                ".job-title",
                ".title"
            ],
            'company': [
                "//span[contains(@class, 'company')]",
                "//div[contains(@class, 'company')]",
                ".company-name",
                ".company"
            ],
            'location': [
                "//span[contains(@class, 'location')]",
                "//div[contains(@class, 'location')]",
                ".location",
                ".job-location"
            ]
        }
        
        for detail_type, xpath_list in selectors.items():
            for xpath in xpath_list:
                try:
                    if xpath.startswith("//"):
                        element = driver.find_element(By.XPATH, xpath)
                    else:
                        element = driver.find_element(By.CSS_SELECTOR, xpath)
                    
                    details[detail_type] = element.text.strip()
                    break
                except NoSuchElementException:
                    continue
        
        return details

