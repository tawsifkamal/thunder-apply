#!/usr/bin/env python3
"""
Thunder Apply - Automated Job Application Tool

A tool to automate job applications using web scraping and form filling.
"""

import logging
import sys
from pathlib import Path
from typing import Dict, List, Optional
import argparse

from selenium_driver import SimplifiedDOMExtractor, WebDriverConfig
from automation_utils import RetryHandler, FormFieldMapper, ElementInteractor, JobApplicationHelper
from config import Config


class ThunderApply:
    """Main application class for automated job applications."""
    
    def __init__(self, config_file: Optional[str] = None):
        """Initialize the Thunder Apply application."""
        self.config = Config(config_file)
        self.config.setup_logging()
        self.logger = logging.getLogger(__name__)
        
        # Initialize components
        self.webdriver_config = WebDriverConfig(
            headless=self.config.webdriver.headless,
            implicit_wait=self.config.webdriver.implicit_wait,
            page_load_timeout=self.config.webdriver.page_load_timeout
        )
        
        self.extractor = None
        self.retry_handler = RetryHandler(
            max_retries=self.config.automation.max_retries,
            delay=self.config.automation.retry_delay
        )
        
        self.profile_data = self.config.get_profile_data()
        self.logger.info("Thunder Apply initialized successfully")
    
    def __enter__(self):
        """Context manager entry."""
        self.extractor = SimplifiedDOMExtractor(self.webdriver_config)
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        if self.extractor:
            self.extractor.close()
    
    def apply_to_job(self, job_url: str, custom_mapping: Optional[Dict] = None) -> bool:
        """Apply to a single job posting."""
        try:
            self.logger.info(f"Starting application process for: {job_url}")
            
            # Load the job page
            self.extractor.load_page(job_url, self.config.automation.page_load_wait)
            
            # Extract job details
            job_details = JobApplicationHelper.extract_job_details(self.extractor.driver)
            self.logger.info(f"Job details: {job_details}")
            
            # Check if this is an application page
            if not JobApplicationHelper.detect_application_form(self.extractor.driver):
                # Look for apply button
                apply_button = JobApplicationHelper.find_apply_button(self.extractor.driver)
                if apply_button:
                    interactor = ElementInteractor(self.extractor.driver, self.retry_handler)
                    if interactor.safe_click(apply_button):
                        self.logger.info("Clicked apply button, waiting for application form...")
                        interactor.wait_for_page_load()
                    else:
                        self.logger.error("Failed to click apply button")
                        return False
                else:
                    self.logger.error("No application form or apply button found")
                    return False
            
            # Create field mapping
            if custom_mapping:
                field_mapping = custom_mapping
            else:
                field_mapping = FormFieldMapper.create_mapping_by_labels(
                    self.extractor.driver, self.profile_data
                )
            
            if not field_mapping:
                self.logger.warning("No field mapping created, attempting basic auto-fill")
                return self._attempt_basic_autofill()
            
            # Fill the form
            success = self._fill_application_form(field_mapping)
            
            if success:
                self.logger.info(f"Successfully applied to job: {job_details.get('title', 'Unknown')}")
            else:
                self.logger.error("Failed to complete job application")
            
            return success
            
        except Exception as e:
            self.logger.error(f"Error applying to job {job_url}: {e}")
            return False
    
    def apply_to_multiple_jobs(self, job_urls: List[str]) -> Dict[str, bool]:
        """Apply to multiple job postings."""
        results = {}
        
        for url in job_urls:
            try:
                results[url] = self.apply_to_job(url)
            except Exception as e:
                self.logger.error(f"Failed to apply to {url}: {e}")
                results[url] = False
        
        # Log summary
        successful = sum(1 for success in results.values() if success)
        total = len(results)
        self.logger.info(f"Application summary: {successful}/{total} successful")
        
        return results
    
    def _fill_application_form(self, field_mapping: Dict) -> bool:
        """Fill the application form using the field mapping."""
        try:
            self.extractor.auto_fill(self.profile_data, field_mapping)
            
            # Look for submit button and click it
            submit_selectors = [
                "//button[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'submit')]",
                "//button[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'apply')]",
                "//input[@type='submit']"
            ]
            
            interactor = ElementInteractor(self.extractor.driver, self.retry_handler)
            
            for selector in submit_selectors:
                try:
                    if interactor.safe_click(("xpath", selector)):
                        self.logger.info("Successfully submitted application")
                        return True
                except Exception:
                    continue
            
            self.logger.warning("Could not find or click submit button")
            return False
            
        except Exception as e:
            self.logger.error(f"Error filling application form: {e}")
            return False
    
    def _attempt_basic_autofill(self) -> bool:
        """Attempt basic autofill using common field patterns."""
        try:
            # Try common field patterns
            common_fields = [
                ("input", "name", "first", self.profile_data.get("first_name", "")),
                ("input", "name", "last", self.profile_data.get("last_name", "")),
                ("input", "name", "email", self.profile_data.get("email", "")),
                ("input", "name", "phone", self.profile_data.get("phone_number", "")),
            ]
            
            success_count = 0
            for element_type, attr_name, attr_value, text in common_fields:
                if text and self.extractor.fill_element_by_type_and_attribute(
                    element_type, attr_name, attr_value, text
                ):
                    success_count += 1
            
            self.logger.info(f"Basic autofill completed {success_count} fields")
            return success_count > 0
            
        except Exception as e:
            self.logger.error(f"Error in basic autofill: {e}")
            return False
    
    def extract_page_structure(self, url: str) -> str:
        """Extract and return the simplified DOM structure of a page."""
        try:
            self.extractor.load_page(url)
            return self.extractor.extract_interactive_elements()
        except Exception as e:
            self.logger.error(f"Error extracting page structure: {e}")
            return ""


def main():
    """Main entry point for the application."""
    parser = argparse.ArgumentParser(description="Thunder Apply - Automated Job Application Tool")
    parser.add_argument("--config", help="Path to configuration file")
    parser.add_argument("--profile", help="Path to profile JSON file", default="profile.json")
    parser.add_argument("--url", help="Single job URL to apply to")
    parser.add_argument("--urls-file", help="File containing list of job URLs")
    parser.add_argument("--extract-only", action="store_true", help="Only extract page structure")
    parser.add_argument("--headless", action="store_true", help="Run in headless mode")
    parser.add_argument("--verbose", "-v", action="store_true", help="Enable verbose logging")
    
    args = parser.parse_args()
    
    # Set up logging level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    try:
        with ThunderApply(args.config) as app:
            if args.extract_only and args.url:
                # Extract page structure only
                structure = app.extract_page_structure(args.url)
                print("Page Structure:")
                print(structure)
                return
            
            if args.url:
                # Apply to single job
                success = app.apply_to_job(args.url)
                sys.exit(0 if success else 1)
            
            elif args.urls_file:
                # Apply to multiple jobs from file
                try:
                    with open(args.urls_file, 'r') as f:
                        urls = [line.strip() for line in f if line.strip()]
                    
                    results = app.apply_to_multiple_jobs(urls)
                    
                    # Print results
                    print("\nApplication Results:")
                    for url, success in results.items():
                        status = "✓" if success else "✗"
                        print(f"{status} {url}")
                    
                    successful = sum(1 for success in results.values() if success)
                    print(f"\nSummary: {successful}/{len(results)} applications successful")
                    
                except FileNotFoundError:
                    print(f"Error: URLs file '{args.urls_file}' not found")
                    sys.exit(1)
            
            else:
                parser.print_help()
                sys.exit(1)
    
    except KeyboardInterrupt:
        print("\nApplication interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

