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

# Ensure the project root is on PYTHONPATH
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

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
    agent.add_task("Click the Sign In button on the login form")
    await agent.step()
    
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
        max_steps=20  # Increased steps since we have more actions to complete
    )
    
    if not task_success:
        print("⚠️ AI couldn't complete the task. You may need to manually select a job and start the application process.")
    else:
        print("✅ Successfully found a job and started the application process")
    
    # Clean up
    await page.wait_for_timeout(100000)
    await agent.close()

if __name__ == '__main__':
    asyncio.run(main())
