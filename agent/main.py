from langchain_openai import ChatOpenAI
from browser_use import Agent
from browser_use.browser.context import BrowserContext
from dotenv import load_dotenv
from util.interactive_agent import InteractiveAgent

load_dotenv()

import asyncio

llm = ChatOpenAI(model="gpt-4o")



async def main():
    # agent = Agent(
    #     task="Look up Fall 2025 internships in the US from Simplify Github",
    #     llm=llm,
    # )
    # result = await agent.run()
    # print(result.extracted_content())
    # BrowserContext.
    agent = InteractiveAgent(
        task="Apply for the job which we have already logged in for now",
        llm=llm,
    )

asyncio.run(main())