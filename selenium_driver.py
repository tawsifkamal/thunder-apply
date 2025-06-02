import time
import json
import logging
from typing import List, Dict, Optional, Union
import traceback
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    NoSuchElementException,
    ElementNotInteractableException,
    TimeoutException,
    WebDriverException,
)

from bs4 import BeautifulSoup

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class WebDriverConfig:
    """Configuration class for WebDriver settings."""
    
    def __init__(self, headless: bool = True, implicit_wait: int = 5, page_load_timeout: int = 30):
        self.headless = headless
        self.implicit_wait = implicit_wait
        self.page_load_timeout = page_load_timeout
        
    def get_chrome_options(self) -> Options:
        """Get configured Chrome options."""
        chrome_options = Options()
        if self.headless:
            chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        return chrome_options


class SimplifiedDOMExtractor:
    """Web automation class for DOM extraction and form filling."""
    
    def __init__(self, config: Optional[WebDriverConfig] = None):
        """Initialize Selenium WebDriver with configuration."""
        self.config = config or WebDriverConfig()
        self.driver = self._initialize_driver()
        logger.info("SimplifiedDOMExtractor initialized successfully")

    def _initialize_driver(self) -> webdriver.Chrome:
        """Initialize and configure the Chrome WebDriver."""
        try:
            chrome_options = self.config.get_chrome_options()
            driver = webdriver.Chrome(options=chrome_options)
            driver.implicitly_wait(self.config.implicit_wait)
            driver.set_page_load_timeout(self.config.page_load_timeout)
            return driver
        except Exception as e:
            logger.error(f"Failed to initialize WebDriver: {e}")
            raise

    def load_page(self, url: str, wait_time: int = 2) -> None:
        """Load the webpage and wait for it to fully load."""
        try:
            logger.info(f"Loading page: {url}")
            self.driver.get(url)
            
            # Wait for page to load completely
            WebDriverWait(self.driver, 10).until(
                lambda driver: driver.execute_script("return document.readyState") == "complete"
            )
            
            # Additional wait for dynamic content
            time.sleep(wait_time)
            logger.info("Page loaded successfully")
            
        except TimeoutException:
            logger.error(f"Timeout while loading page: {url}")
            raise
        except Exception as e:
            logger.error(f"Error loading page {url}: {e}")
            raise

    def extract_interactive_elements(self) -> str:
        """Extract interactive elements and simplify the DOM."""
        try:
            logger.info("Extracting interactive elements from page")
            
            # Get the page source after any dynamic content has loaded
            html_content = self.driver.page_source
            
            # Parse the HTML with BeautifulSoup
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Process iframes
            self._process_iframes(soup)
            
            # Simplify the main soup
            simplified_dom = self._simplify_dom(soup)
            
            logger.info("DOM extraction completed successfully")
            return simplified_dom.prettify()
            
        except Exception as e:
            logger.error(f"Error extracting interactive elements: {e}")
            raise

    def _process_iframes(self, soup: BeautifulSoup) -> None:
        """Process all iframes in the page and extract their content."""
        iframe_tags = soup.find_all('iframe')
        
        for index, iframe_tag in enumerate(iframe_tags):
            iframe_identifier = self._get_iframe_identifier(iframe_tag, index)
            
            try:
                # Switch to the iframe
                self.driver.switch_to.frame(iframe_identifier)
                
                # Get the iframe's page source
                iframe_html_content = self.driver.page_source
                iframe_soup = BeautifulSoup(iframe_html_content, 'html.parser')
                
                # Simplify the iframe soup
                simplified_iframe_soup = self._simplify_dom(iframe_soup)
                
                # Replace the iframe tag with the simplified content
                iframe_tag.replace_with(simplified_iframe_soup)
                
                # Switch back to the default content
                self.driver.switch_to.default_content()
                
                logger.debug(f"Successfully processed iframe: {iframe_identifier}")
                
            except Exception as e:
                logger.warning(f"Error processing iframe '{iframe_identifier}': {e}")
                self.driver.switch_to.default_content()
                continue

    def _get_iframe_identifier(self, iframe_tag, index: int) -> Union[str, int]:
        """Get the identifier for an iframe (id, name, or index)."""
        iframe_id = iframe_tag.get('id')
        iframe_name = iframe_tag.get('name')
        
        if iframe_id:
            return iframe_id
        elif iframe_name:
            return iframe_name
        else:
            return index

    def _simplify_dom(self, soup: BeautifulSoup) -> BeautifulSoup:
        """Simplify the DOM while preserving important nested tags."""
        from bs4 import NavigableString

        # Define the tags that are interactive or important
        interactive_tags = ['a', 'button', 'form', 'input', 'select', 'textarea', 'label']
        important_tags = ['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p', 'span']
        tags_to_keep = set(interactive_tags + important_tags)

        # Collect all tags to process
        all_tags = soup.find_all(True)
        tags_to_process = all_tags.copy()

        for tag in tags_to_process:
            if tag.name == 'option':
                # Remove 'option' tags
                tag.decompose()
                continue

            if tag.name not in tags_to_keep:
                # Find all descendants that are in tags_to_keep
                important_descendants = tag.find_all(tags_to_keep)
                if important_descendants:
                    # Insert important descendants before the current tag
                    for descendant in important_descendants:
                        tag.insert_before(descendant)
                    # Remove the current tag
                    tag.decompose()
                else:
                    # Check for NavigableStrings (text content)
                    if any(isinstance(child, NavigableString) for child in tag.contents):
                        # Replace the tag with its text content
                        tag.replace_with(tag.get_text())
                    else:
                        # Remove the tag entirely
                        tag.decompose()
        return soup

    def auto_fill(self, profile: Dict, mapping: Dict) -> None:
        """Fill in form fields using the provided mapping and profile data."""
        logger.info("Starting auto-fill process")
        
        for key, value in mapping.items():
            try:
                if isinstance(value, dict) and "id" in value:
                    element = self.driver.find_element(By.ID, value["id"])
                    
                    if value.get("type") == "input":
                        if key in profile:
                            element.clear()
                            element.send_keys(profile[key])
                            logger.debug(f"Filled input field '{key}' with value from profile")
                        else:
                            logger.warning(f"Profile key '{key}' not found")
                            
                    elif value.get("type") == "file":
                        if "resume_path" in profile:
                            element.send_keys(profile["resume_path"])
                            logger.debug(f"Uploaded file: {profile['resume_path']}")
                        else:
                            logger.warning("Resume path not found in profile")
                    else:
                        logger.warning(f"Unknown field type: {value.get('type')}")
                        
            except NoSuchElementException:
                logger.error(f"Element with ID '{value.get('id')}' not found")
            except Exception as e:
                logger.error(f"Error filling field '{key}': {e}")

    def click_element_by_type_and_text(self, element_type: str, text: str, timeout: int = 3) -> bool:
        """Click an element based on its type and visible text content."""
        try:
            xpath = (
                f"//{element_type}[contains(translate(normalize-space(.), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), "
                f"'{text.lower()}')]"
            )

            # Wait until the element is clickable
            element = WebDriverWait(self.driver, timeout).until(
                EC.element_to_be_clickable((By.XPATH, xpath))
            )

            # Scroll to the element
            self.driver.execute_script("arguments[0].scrollIntoView(true);", element)

            # Click the element
            element.click()

            # Wait for any actions to complete
            time.sleep(1)
            
            logger.info(f"Successfully clicked {element_type} with text '{text}'")
            return True
            
        except TimeoutException:
            logger.error(f"Timeout: Element '{element_type}' with text '{text}' not found or not clickable.")
            return False
        except NoSuchElementException:
            logger.error(f"Element '{element_type}' with text '{text}' not found.")
            return False
        except ElementNotInteractableException:
            logger.error(f"Element '{element_type}' with text '{text}' is not interactable.")
            return False
        except Exception as e:
            logger.error(f"An unexpected error occurred while clicking element '{element_type}' with text '{text}': {e}")
            traceback.print_exc()
            return False

    def fill_element_by_type_and_attribute(
        self,
        element_type: str,
        attribute_name: str,
        attribute_value: str,
        text: str,
        exact_match: bool = True,
        timeout: int = 10
    ) -> bool:
        """Fill an input or textarea element based on its type and a specific attribute."""
        try:
            # Build the XPath expression with case-insensitive contains
            xpath = (
                f"//{element_type}[contains(translate(@{attribute_name}, 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), "
                f"'{attribute_value.lower()}')]"
            )

            # Wait until the element is present and visible
            element = WebDriverWait(self.driver, timeout).until(
                EC.visibility_of_element_located((By.XPATH, xpath))
            )

            # Scroll to the element
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)

            # Clear any existing text
            element.clear()

            # Input the specified text
            element.send_keys(text)

            # Wait briefly to ensure text is entered
            time.sleep(0.5)
            
            logger.info(f"Successfully filled {element_type} with {attribute_name}='{attribute_value}'")
            return True
            
        except TimeoutException:
            logger.error(
                f"Timeout: Element '{element_type}' with {attribute_name}='{attribute_value}' "
                "not found or not interactable."
            )
            return False
        except NoSuchElementException:
            logger.error(
                f"Element '{element_type}' with {attribute_name}='{attribute_value}' not found."
            )
            return False
        except ElementNotInteractableException:
            logger.error(
                f"Element '{element_type}' with {attribute_name}='{attribute_value}' is not interactable."
            )
            return False
        except Exception as e:
            logger.error(
                f"An unexpected error occurred while filling element '{element_type}' "
                f"with {attribute_name}='{attribute_value}': {e}"
            )
            traceback.print_exc()
            return False

    def close(self) -> None:
        """Close the Selenium WebDriver."""
        try:
            if self.driver:
                self.driver.quit()
                logger.info("WebDriver closed successfully")
        except Exception as e:
            logger.error(f"Error closing WebDriver: {e}")


# Example usage:
if __name__ == "__main__":
    # Configuration
    config = WebDriverConfig(headless=True)
    
    # Initialize extractor
    extractor = SimplifiedDOMExtractor(config)
    
    try:
        # Load a test page
        url = "https://www.example.com"  # Replace with the URL you want to test
        extractor.load_page(url)
        
        # Extract simplified DOM
        simplified_dom = extractor.extract_interactive_elements()
        print("Simplified DOM:")
        print(simplified_dom)
        
        # Example interactions
        # extractor.click_element_by_type_and_text("button", "submit")
        # extractor.fill_element_by_type_and_attribute("input", "name", "email", "test@example.com")
        
    except Exception as e:
        logger.error(f"Error in main execution: {e}")
    finally:
        # Close the browser when done
        extractor.close()

