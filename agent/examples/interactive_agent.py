#!/usr/bin/env python3
"""
Example script demonstrating InteractiveAgent usage with fine-grained control.
"""
import os
import sys
import asyncio
from dotenv import load_dotenv

# Ensure the project root is on PYTHONPATH
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from langchain_openai import ChatOpenAI
from ..util.interactive_agent import InteractiveAgent

load_dotenv()

async def manual_callback(agent: InteractiveAgent) -> None:
    """
    Invoked whenever the agent is in manual mode.
    Prompts the user to type a message, then injects it or resumes AI.
    """
    prompt = input("🔧 Manual> ")
    if prompt.strip():
        # Run exactly one AI step with this custom prompt
        await agent.step_with_prompt(prompt)
    else:
        # Empty input: resume full AI-driven loop
        agent.enable_agent()

async def main():
    # Initialize LLM (replace model name/API as needed)
    llm = ChatOpenAI(model='gpt-4o', temperature=0.0)
    task = "Go to github.com/login"

    # Create an InteractiveAgent and start in manual mode
    agent = InteractiveAgent(task=task, llm=llm)

    # Start the agent in manual mode
    agent.disable_agent()

    # Begin interactive loop: manual_callback drives manual steps
    await agent.run_interactive(manual_callback, max_steps=10)

    # After exiting interactive loop, add a new subtask
    agent.add_task("Now take a screenshot of the page")
    # Enable AI to execute the next step automatically
    agent.enable_agent()
    await agent.step()

    # Print the full action/history log
    print("\n=== Agent History ===")
    for entry in agent.state.history.history:
        print(entry)

if __name__ == '__main__':  # pragma: no cover
    asyncio.run(main())