import asyncio
import json
from playwright.async_api import async_playwright

async def main():
    url = "https://athenahealth.wd1.myworkdayjobs.com/en-US/External/job/Boston-MA/XMLNAME-2025-Summer-Software-Engineering-Intern_R11181-1?utm_source=Simplify&ref=Simplify"
    defaultPassword = "ahbuhYb578#"
    headless = False
    slo_mo = 60

    # Load data from a JSON file
    with open('profile.json', 'r') as file:
        dict = json.load(file)

    async with async_playwright() as p_driver:
        browser = await p_driver.chromium.launch(headless=headless, slow_mo=slo_mo) # Change this later
        page = await browser.new_page()
        await page.goto(url=url)
        # page.screenshot(path="image") # To take a screenshot of the web page
        
        """Click the Apply Button"""
        await page.get_by_role("button", name="Apply").click()

        """Click the Apply Manually Button"""
        await page.get_by_role("button", name="Apply Manually").click()

        """Try to sign in with an existing account"""
        await page.get_by_label("Email Address").fill(dict["email"])
        await page.get_by_label("Password").fill(defaultPassword)

        """If the Sign-In doesn't work, an account needs to be created"""
        alert_element = await page.get_by_role("alert").filter(has_text="wrong")
        if alert_element:
            await page.get_by_role("button", name="Create Account").click()
            await page.get_by_label("Email Address").fill(dict["email"])
            await page.get_by_label("Password").fill(defaultPassword)
            await page.get_by_label("Verify New Password").fill(defaultPassword)

        else:
            """If the Sign-In does work"""



        await browser.close()

asyncio.run(main())