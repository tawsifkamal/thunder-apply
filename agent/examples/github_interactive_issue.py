"""
github_fallback_login_issue.py

Example: let the AI navigate to a GitHub repo and open Issues, but fallback to manual login
and manual click if the step fails due to not being authenticated.
"""
import asyncio
import os
from dotenv import load_dotenv

from langchain_openai import ChatOpenAI
from ..util.interactive_agent import InteractiveAgent


async def manual_fallback(agent: InteractiveAgent) -> None:
    """
    Fallback callback: if redirected to login, perform login; otherwise click Issues/New issue.
    """
    page = await agent.browser_context.get_current_page()
    url = page.url
    print(f"⚠️ Fallback triggered on URL: {url}")
    # If on login page, ask for credentials and sign in
    if 'github.com/login' in url:
        from getpass import getpass
        print("🔧 Manual: logging into GitHub")
        username = os.getenv('GITHUB_USERNAME') or input('GitHub username: ')
        password = os.getenv('GITHUB_PASSWORD') or getpass('GitHub password: ')
        await page.fill("input[name='login']", username)
        await page.fill("input[name='password']", password)
        await page.click("input[name='commit']")
        await page.wait_for_load_state('networkidle')
        print("✅ Logged in manually")
    else:
        # Otherwise, click Issues and New issue via code
        print("🔧 Manual: clicking 'Issues' and 'New issue'")
        await page.click("a[href$='/issues']")
        await page.wait_for_load_state('networkidle')
        await page.click("a[href$='/issues/new']")
        await page.wait_for_load_state('networkidle')
        print("✅ Navigated to New Issue form")
    # After fixing, re-enable AI control
    agent.enable_agent()


async def main():
    # Load env for repo/credentials
    load_dotenv()
    repo = os.getenv('GITHUB_REPO')
    issue_title = 'Test issue via fallback'
    issue_body = 'This issue was created after manual fallback.'

    # Initialize LLM and agent
    llm = ChatOpenAI(model='gpt-4o', temperature=0)
    task = (
        f"On GitHub {repo}, create a new issue titled '{issue_title}' with body '{issue_body}'."
    )
    agent = InteractiveAgent(task=task, llm=llm)

    # manually login via playwright commands
    page = await agent.browser_context.get_current_page()
    # Go to login page and sign in
    print("🔧 Manual: logging into GitHub")
    await page.goto('https://github.com/login')
    username = os.getenv('GITHUB_USERNAME') or input('GitHub username: ')
    from getpass import getpass
    password = os.getenv('GITHUB_PASSWORD') or getpass('GitHub password: ')
    await page.fill("input[name='login']", username)
    await page.fill("input[name='password']", password)
    await page.click("input[name='commit']")

    print(f"🔧 Manual: navigating to {repo}")
    await page.goto(repo + "/issues")
    # await page.wait_for_load_state('networkidle')
    print("✅ At Issues page manually")

    # Now hand control to the agent: it will only need to create the issue
    # It will still fallback on login redirects or other click failures
    await agent.run_interactive(manual_fallback, max_steps=2)

    # Close browser
    await agent.close()


if __name__ == '__main__':
    asyncio.run(main())