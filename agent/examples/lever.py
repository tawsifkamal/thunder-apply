#!/usr/bin/env python3
"""
Using this link:
https://jobs.lever.co/leverdemo193/1be72529-55a2-448d-84f6-b6db3611b19e?utm_campaign=google_jobs_apply&utm_source=google_jobs_apply&utm_medium=organic
"""
import os
import sys
import asyncio
from dotenv import load_dotenv

from langchain_openai import ChatOpenAI
from ..util.interactive_agent import InteractiveAgent
from ..util.user_data import UserData

load_dotenv()

async def wait_for_page_load(page, timeout=30000):
    """
    Wait for page to be fully loaded with multiple conditions.
    """
    try:
        # Wait for network to be idle
        await page.wait_for_load_state('networkidle', timeout=timeout)
        # Wait for DOM to be ready
        await page.wait_for_load_state('domcontentloaded', timeout=timeout)
        # Additional wait to ensure dynamic content is loaded
        await page.wait_for_timeout(2000)  # 2 second buffer
        return True
    except Exception as e:
        print(f"⚠️ Warning: Page load wait timed out or failed: {e}")
        return False

async def is_job_details_page(agent: InteractiveAgent) -> bool:
    """
    Check if we're on a job details page AND have started the actual application process.
    
    The workflow is:
    1. Click on a job listing
    2. Click Apply button
    3. Get redirected to the actual application form
    
    We consider success when we're on the actual application form.
    """
    page = await agent.get_agent_current_page()
    current_url = page.url
    
    # Check if we're on a job details page
    if '/jobs/' not in current_url:
        return False
        
    # Check if we're on the actual application form
    # Look for common application form elements
    try:
        form_elements = await page.query_selector_all('form, input[type="text"], input[type="email"], textarea')
        if form_elements and len(form_elements) > 0:
            # We found form elements, we're probably on the application form
            return True
    except Exception as e:
        print(f"⚠️ Error checking for form elements: {e}")
    
    return False

async def upload_resume(page) -> bool:
    """
    Manually handle resume upload using Playwright's file input functionality.
    Looks for resume in the same directory as the script first, then falls back to environment variable or prompt.
    
    Args:
        page: The Playwright page object
    
    Returns:
        bool: True if upload was successful, False otherwise
    """
    try:
        print("🔧 Manual: Handling resume upload...")
        
        # Wait for the file input to be visible using the exact XPath
        file_input_xpath = "//input[@class='application-file-input invisible-resume-upload' and @data-qa='input-resume']"
        file_input = page.locator(file_input_xpath)
        await file_input.wait_for(state='visible', timeout=5000)
        
        # First try to find resume in the same directory as the script
        script_dir = os.path.dirname(os.path.abspath(__file__))
        local_resume = os.path.join(script_dir, "resume.pdf")
        
        # Get the resume path, trying different sources in order:
        # 1. Local directory
        # 2. Environment variable
        # 3. User input
        if os.path.exists(local_resume):
            resume_path = local_resume
            print("📄 Found resume in script directory")
        else:
            resume_path = os.getenv('RESUME_PATH')
            if not resume_path:
                resume_path = input('Enter the full path to your resume file: ')
            
        if not os.path.exists(resume_path):
            print(f"⚠️ Resume file not found at: {resume_path}")
            return False
            
        print(f"📄 Uploading resume from: {resume_path}")
        
        # Set the file input value
        await file_input.set_input_files(resume_path)
        
        # Wait for upload to complete
        await page.wait_for_timeout(2000)  # Wait for upload to start
        
        # Check for upload success
        try:
            # Wait for either a success message or the next button to be enabled
            # Adjust these selectors based on Lever's actual implementation
            success_locator = page.locator('.upload-success, .file-upload-success, button:not([disabled])')
            await success_locator.wait_for(state='visible', timeout=5000)
            print("✅ Resume uploaded successfully")
            return True
        except Exception as e:
            print(f"⚠️ Could not confirm upload success: {e}")
            return False
            
    except Exception as e:
        print(f"⚠️ Error during resume upload: {e}")
        return False

async def handle_bot_detection(page):
    """
    Handle any bot detection challenges that might appear.
    """
    try:
        # Check for common bot detection elements
        # This will need to be adjusted based on Lever's specific implementation
        bot_challenge = await page.query_selector('.challenge-container, .captcha-container, .recaptcha')
        if bot_challenge:
            print("⚠️ Bot detection challenge detected!")
            print("Please complete the challenge manually...")
            
            # Wait for the challenge to be completed
            # This might need to be adjusted based on how Lever handles it
            await page.wait_for_selector('.challenge-container, .captcha-container, .recaptcha', 
                                       state='hidden',
                                       timeout=60000)  # Give user 60 seconds to complete
            print("✅ Challenge completed")
            return True
            
        return False
    except Exception as e:
        print(f"⚠️ Error handling bot detection: {e}")
        return False

async def main():
    # Initialize LLM
    llm = ChatOpenAI(model='gpt-4o', temperature=0.0)
    
    # Initial task to navigate to Lever careers
    task = "Navigate to the careers page and find software engineering internships"
    agent = InteractiveAgent(task=task, llm=llm)
    
    # Start in manual mode
    agent.disable_agent()
    
    # Get the page for manual operations
    page = await agent.get_agent_current_page()
    
    # Navigate to careers page
    initial_url = "https://jobs.lever.co/leverdemo193/1be72529-55a2-448d-84f6-b6db3611b19e?utm_campaign=google_jobs_apply&utm_source=google_jobs_apply&utm_medium=organic"
    await page.goto(initial_url, wait_until='domcontentloaded')
    await page.wait_for_timeout(2000)
    print("found job")
    
    # Check for bot detection
    await handle_bot_detection(page)
    
    # Click the Apply button directly using XPath
    print("Clicking Apply button...")
    apply_button_xpath = "//a[@class='postings-btn template-btn-submit cerulean' and @data-qa='show-page-apply']"
    await page.click(apply_button_xpath)
    
    # Wait for the application form to load
    await page.wait_for_timeout(2000)
    
    # Check for bot detection again before proceeding
    await handle_bot_detection(page)
    

    # TODO
    # Handle resume upload manually
    upload_success = await upload_resume(page)
    if not upload_success:
        print("⚠️ Resume upload failed. You may need to upload it manually.")
        await agent.close()
        return



    print("✅ Resume uploaded successfully")
    
    # Let AI continue with the rest of the application? I think we can hardcode everything
    name_path = "//*[@id='application-form']/div[1]/ul/li[2]/label/div[2]/input"
    await page.fill(name_path, "Prama Yudhistira")
    agent.enable_agent()
    
    await agent.run_ai_task(
        task="Complete the rest of the application form",
        success_condition=lambda agent: False,  # We'll need to define a proper success condition
        max_steps=30
    )
    
    # Clean up
    await page.wait_for_timeout(1000000) #for sake of testing
    await agent.close()

if __name__ == '__main__':
    asyncio.run(main())
