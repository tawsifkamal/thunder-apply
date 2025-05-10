#!/usr/bin/env python3
"""
Script for applying to NVIDIA jobs using InteractiveAgent.
Handles Workday login and job application process.
"""
import os
import sys
import asyncio
from dotenv import load_dotenv
from getpass import getpass

from langchain_openai import ChatOpenAI
from ..util.interactive_agent import InteractiveAgent

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

async def manual_login(agent: InteractiveAgent) -> None:
    """
    Always perform manual login to Workday, regardless of current URL.

    TODO: Find out why manually clicking login button doesn't work
    """
    page = await agent.get_agent_current_page()
    print("🔧 Manual: logging into Workday")
    
    # Always go to login page first
    await page.goto("https://nvidia.wd5.myworkdayjobs.com/NVIDIAExternalCareerSite/login", wait_until='domcontentloaded')
    await page.wait_for_timeout(2000)  # Wait 2 seconds for page to stabilize
    
    # Get credentials
    username = os.getenv('WORKDAY_USERNAME') or input('Workday username: ')
    password = os.getenv('WORKDAY_PASSWORD') or getpass('Workday password: ')
    
    print("logging in with: ", os.getenv('WORKDAY_USERNAME'))
    
    # Wait for and fill email field
    await page.wait_for_selector('input[data-automation-id="email"]', state='visible')
    await page.fill('input[data-automation-id="email"]', username)
    await page.wait_for_timeout(500)  # Wait 0.5 seconds between fields
    
    # Wait for and fill password field
    await page.wait_for_selector('input[data-automation-id="password"]', state='visible')
    await page.fill('input[data-automation-id="password"]', password)
    await page.wait_for_timeout(500)  # Wait 0.5 seconds before clicking
    
    # Let AI handle the login button click
    print("Letting AI handle the login button click...")
    agent.enable_agent()
    await agent.run_single_step("Click the Sign In button on the login form") #before i did agent.add_task and agent.step
    
    # Switch back to manual control
    agent.disable_agent()
    await page.wait_for_timeout(2000)  # Wait 2 seconds for navigation to start
    
    # Verify login success
    current_url = page.url
    if 'login' in current_url.lower():
        print("⚠️ Login may have failed.")
        return False
    return True

async def manual_callback(agent: InteractiveAgent) -> None:
    """
    Handle manual interactions and provide guidance to the agent.
    I honestly don't know why I wrote this callback, agent will most likely not fail...
    """
    prompt = input("🔧 Manual> ")
    if prompt.strip():
        # Run one AI step with custom prompt
        await agent.step_with_prompt(prompt)
    else:
        # Resume AI control
        agent.enable_agent()

async def is_job_details_page(agent: InteractiveAgent) -> bool:
    """
    Check if we're on a job details page AND have started the actual application process.
    
    The workflow is:
    1. Click Apply button -> Shows popup with options
    2. Select an application method (resume/last application/manual)
    3. Get redirected to the actual application form
    
    We consider success when we're on the actual application form.
    """
    page = await agent.get_agent_current_page()
    current_url = page.url
    
    # First check if we're on a job details page
    if '/job/' not in current_url:
        return False

    return True

#TODO: this works for any xpath, make this constant and work for any file input
#      refactor later
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
        
        x_path_pdf = '//*[@id="root"]/div/div/div[2]/div/main/div/div[3]/div[1]/div[2]/p/div/div/div[1]/div[2]/div[1]/input'
        file_input = page.locator(x_path_pdf)
        # await file_input.wait_for(state='visible', timeout=5000)
        print("found file input at: ", file_input)
        
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

        return True
        
            
    except Exception as e:
        print(f"⚠️ Error during resume upload: {e}")
        return False

async def main():
    # Initialize LLM
    llm = ChatOpenAI(model='gpt-4o', temperature=0.0)
    
    # Initial task to navigate to NVIDIA careers
    task = "Navigate to NVIDIA careers page and find software engineering internships"
    agent = InteractiveAgent(task=task, llm=llm)
    
    # Start in manual mode for login
    agent.disable_agent()
    
    # Get the page for manual operations
    page = await agent.get_agent_current_page()
    
    # Always perform manual login first
    login_success = await manual_login(agent)
    if not login_success:
        print("❌ Login failed. Exiting...")
        await agent.close()
        return
    
    print("✅ Logged in successfully")
    
    # Navigate to careers page after successful login
    print("🔧 Manual: navigating to NVIDIA careers")
    await page.goto("https://nvidia.wd5.myworkdayjobs.com/NVIDIAExternalCareerSite", wait_until='domcontentloaded')
    await page.wait_for_timeout(2000)
    
    # Let AI handle finding and clicking on an internship
    task_success = await agent.run_ai_task(
        task="Search for any internships, click on the first relevant position, click the Apply button, and select 'Apply with Resume' to start the actual application process",
        success_condition=is_job_details_page,
        max_steps=20
    )
    
    if not task_success:
        print("⚠️ AI couldn't complete the task. You may need to manually select a job and start the application process.")
        await agent.close()
        return
        
    print("✅ Successfully found a job and started the application process")
    
    # Handle resume upload manually
    upload_success = await upload_resume(page)
    if not upload_success:
        print("⚠️ Resume upload failed. You may need to upload it manually.")
        await agent.close()
        return
        
    print("✅ Resume uploaded successfully")
    
    
    #TODO: Implement the rest of the application form
    #      Perhaps manual for known fields, ai to check for the rest
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
