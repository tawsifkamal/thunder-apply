import time
import json
from typing import List, Dict
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
)

from bs4 import BeautifulSoup

class WorkdayDOMExtractor:
    def __init__(self, headless: bool = True):
        """Initialize Selenium WebDriver."""
        chrome_options = Options()
        if headless:
            chrome_options.add_argument("--headless")
        self.driver = webdriver.Chrome(options=chrome_options)
        self.driver.implicitly_wait(5)  # Wait up to 5 seconds for elements to appear. There may be issues when using implicit and explicit waits.
        self.TIMEOUT = 3

    def load_page(self, url: str):
        """Load the webpage."""
        self.driver.get(url)

        time.sleep(2)  # Wait for the page to load completely

    def check_xpath_exists(self, xpath: str):
        try:
            element = WebDriverWait(self.driver, self.TIMEOUT).until(
                EC.visibility_of_element_located((By.XPATH, xpath))
            )
            return element
        except NoSuchElementException:
            return False
    
    def extract_interactive_elements(self) -> str:
        """Extract interactive elements and simplify the DOM."""
        # Get the page source after any dynamic content has loaded
        html_content = self.driver.page_source
        
        """Click the Apply Button"""
        # apply_xpath = "//a[@role='button']"
        apply_xpath = "//a[text()='Apply']"
        element = WebDriverWait(self.driver, self.TIMEOUT).until(
            EC.element_to_be_clickable((By.XPATH, apply_xpath))
        )
        # Click the Apply Button
        element.click()

        """Click the Apply Manually Button"""
        apply_manually_xpath = "//a[text()='Apply Manually']"
        element = WebDriverWait(self.driver, self.TIMEOUT).until(
            EC.element_to_be_clickable((By.XPATH, apply_manually_xpath))
        )
        # Click the Apply Manually Button
        element.click()

        """Try to sign in with an existing account"""
        sign_in_xpath = "//form[contains(@data-automation-id,'signIn')]"
        email_xpath = sign_in_xpath + "//input[contains(@data-automation-id, 'email')]"
        password_xpath = sign_in_xpath + "//input[contains(@data-automation-id, 'password')]"
        si_xpath = sign_in_xpath + "//button[@type='submit']"

        # Wait until the elements are present and visible
        email_field = WebDriverWait(self.driver, self.TIMEOUT).until(
            EC.visibility_of_element_located((By.XPATH, email_xpath))
        )
        password_field = WebDriverWait(self.driver, self.TIMEOUT).until(
            EC.visibility_of_element_located((By.XPATH, password_xpath))
        )
        si_button = WebDriverWait(self.driver, self.TIMEOUT).until(
            EC.visibility_of_element_located((By.XPATH, si_xpath))
        )

        # Clear any existing text
        email_field.clear()
        password_field.clear()

        # Input the specified text
        default_email = "tabbaa.abdulrahman1@gmail.com" ############################################################### RETURN TO THIS LATER #########################
        default_password = "Runner400" ############################################################### RETURN TO THIS LATER #########################
        email_field.send_keys(default_email)
        password_field.send_keys(default_password)

        # Wait briefly to ensure text is entered
        time.sleep(0.5)

        # Scroll to and click the Sign In button
        self.driver.execute_script("arguments[0].scrollIntoView(true);", si_button)
        # Wait a little longer to guarantee no interruptions when clicking the button
        time.sleep(1)
        si_button.click()

        """If Sign-In doesn't work, a pop-up will show up, and an account needs to be created"""
        si_error_xpath = "//div[@role='alert']"
        si_error_element = self.check_xpath_exists(si_error_xpath)
        if not si_error_element:
            # account_xpath = "//button[text()='Create Account']"
            account_xpath = "//button[contains(text(), 'Create Account')]" # IDK if this works. If not, use above line
            element = WebDriverWait(self.driver, self.TIMEOUT).until(
                EC.element_to_be_clickable((By.XPATH, account_xpath))
            )
            # Click the Create Account Button
            element.click()

            """Create a new account"""
            create_ac_xpath = "//form[contains(@data-automation-id, 'signInForm')]"
            element = WebDriverWait(self.driver, self.TIMEOUT).until(
                EC.element_to_be_clickable((By.XPATH, account_xpath))
            )


        
        
        
        
        
        
        # # Parse the HTML with BeautifulSoup
        # soup = BeautifulSoup(html_content, 'html.parser')

        #         # Find all iframes in the soup
        # iframe_tags = soup.find_all('iframe') # By default, considers all soup's children, not just immediate children

        # for index, iframe_tag in enumerate(iframe_tags):
        #     # Get the iframe's id, name, or index
        #     iframe_id = iframe_tag.get('id')
        #     iframe_name = iframe_tag.get('name')
        #     iframe_src = iframe_tag.get('src')

        #     # Determine how to identify the iframe
        #     if iframe_id:
        #         iframe_identifier = iframe_id
        #     elif iframe_name:
        #         iframe_identifier = iframe_name
        #     else:
        #         # If no id or name, use the index
        #         iframe_identifier = index

        #     try:
        #         # Switch to the iframe
        #         self.driver.switch_to.frame(iframe_identifier)
        #         # Get the iframe's page source
        #         iframe_html_content = self.driver.page_source
        #         # Parse the iframe's content
        #         iframe_soup = BeautifulSoup(iframe_html_content, 'html.parser')
        #         # Simplify the iframe soup
        #         simplified_iframe_soup = self._simplify_dom(iframe_soup)
        #         # Replace the iframe tag in the main soup with the simplified iframe content
        #         iframe_tag.replace_with(simplified_iframe_soup)
        #         # Switch back to the default content
        #         self.driver.switch_to.default_content()
        #     except Exception as e:
        #         print(f"Error processing iframe '{iframe_identifier}': {e}")
        #         self.driver.switch_to.default_content()
        #         continue

        # # Now simplify the main soup
        # simplified_dom = self._simplify_dom(soup)

        # return simplified_dom.prettify()
        
        return "Success"


    def _simplify_dom(self, soup: BeautifulSoup) -> BeautifulSoup:
        """Simplify the DOM while preserving important nested tags."""
        from bs4 import NavigableString

        # Define the tags that are interactive or important
        interactive_tags = ['a', 'button', 'form', 'input', 'select', 'textarea', 'label']
        important_tags = ['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p', 'span']
        tags_to_keep = set(interactive_tags + important_tags)

        # Collect all tags to process
        all_tags = soup.find_all(True)

        # Since we're modifying the tree, make a copy of the tags to process
        tags_to_process = all_tags.copy()

        for tag in tags_to_process:
            if tag.name == 'option':
                # Remove 'option' tags
                tag.decompose()

                continue  # Move to the next tag

            if tag.name not in tags_to_keep:
                # Find all descendants that are in tags_to_keep
                important_descendants = tag.find_all(tags_to_keep)
                if important_descendants: ################################### Shouldn't we loop down the tree to find important descendants instead of just checking immediate children?
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
    
    def auto_fill(self, profile, mapping):
        # Fill in the form fields using the mapping
        for key, value in mapping.items():
            if isinstance(value, dict) and "id" in value:
                element = self.driver.find_element(by = By.ID)
                if value["type"] == "input":
                    element.send_keys(profile[key])
                elif value["type"] == "file":
                    element.send_keys(profile["resume_path"])  # for file upload

    
    def click_element_by_type_and_text(self, element_type: str, text: str):
        """Click an element based on its type and visible text content."""
        try:
            xpath = (
                f"//{element_type}[contains(translate(normalize-space(.), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), "
                f"'{text.lower()}')]"
            )

            # Wait until the element is clickable
            element = WebDriverWait(self.driver, self.TIMEOUT).until(
                EC.element_to_be_clickable((By.XPATH, xpath))
            )

            # Scroll to the element
            self.driver.execute_script("arguments[0].scrollIntoView(true);", element)

            # Click the element
            element.click()

            # Wait for any actions to complete (adjust as necessary)
            time.sleep(1)
        except TimeoutException:
            print(f"Timeout: Element '{element_type}' with text '{text}' not found or not clickable.")
        except NoSuchElementException:
            print(f"Element '{element_type}' with text '{text}' not found.")
        except ElementNotInteractableException:
            print(f"Element '{element_type}' with text '{text}' is not interactable.")
        except Exception as e:
            print(f"An unexpected error occurred while clicking element '{element_type}' with text '{text}': {e}")
            traceback.print_exc()

    def fill_element_by_type_and_attribute(
        self,
        element_type: str,
        attribute_name: str,
        attribute_value: str,
        text: str,
        exact_match: bool = True
    ):
        """Fill an input or textarea element based on its type and a specific attribute."""
        try:
            # Build the XPath expression with case-insensitive contains
            xpath = (
                f"//{element_type}[contains(translate(@{attribute_name}, 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), "
                f"'{attribute_value.lower()}')]"
            )

            # Wait until the element is present and visible
            element = WebDriverWait(self.driver, self.TIMEOUT).until(
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
        except TimeoutException:
            print(
                f"Timeout: Element '{element_type}' with {attribute_name}='{attribute_value}' "
                "not found or not interactable."
            )
        except NoSuchElementException:
            print(
                f"Element '{element_type}' with {attribute_name}='{attribute_value}' not found."
            )
        except ElementNotInteractableException:
            print(
                f"Element '{element_type}' with {attribute_name}='{attribute_value}' is not interactable."
            )
        except Exception as e:
            print(
                f"An unexpected error occurred while filling element '{element_type}' "
                f"with {attribute_name}='{attribute_value}': {e}"
            )
            traceback.print_exc()

    def close(self):
        """Close the Selenium WebDriver."""
        self.driver.quit()

# Example usage:
if __name__ == "__main__":
    url = "https://athenahealth.wd1.myworkdayjobs.com/en-US/External/job/Boston-MA/XMLNAME-2025-Summer-Software-Engineering-Intern_R11181-1?utm_source=Simplify&ref=Simplify"  # Replace with the URL you want to test

    extractor = None
    """Determine which common application software is being used"""
    if url.find("workday") != -1:
        extractor = WorkdayDOMExtractor(headless=False)
    
    # extractor = WorkdayDOMExtractor(headless=True)
    extractor.load_page(url)
    # simplified_dom = extractor.extract_interactive_elements()
    print(extractor.extract_interactive_elements())
    # print("Simplified DOM:")
    # print(simplified_dom)

    # # Interact with the page (example)
    # extractor.click_button_by_id("interactive-1")
    # extractor.fill_input_by_id("interactive-2", "Sample text")

    # Close the browser when done
    extractor.close()
