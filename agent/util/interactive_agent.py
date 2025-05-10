"""
interactive_agent.py

Subclass of Agent that supports switching between manual and AI-driven control.
"""
import asyncio
from typing import Callable, Any, Optional

from browser_use.agent.service import Agent, AgentStepInfo
from langchain_core.messages import HumanMessage


class InteractiveAgent(Agent):
    """
    An Agent that can be paused for manual interaction and resumed for AI-driven steps.
    """
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        # When False, step() is a no-op until enable_agent() is called.
        self._agent_enabled: bool = True

    def disable_agent(self) -> None:
        """
        Enter manual mode: steps will not be driven by the AI.
        """
        self._agent_enabled = False

    def enable_agent(self) -> None:
        """
        Resume AI-driven mode: subsequent steps will be executed by the AI.
        """
        self._agent_enabled = True

    async def step(self, step_info: Optional[AgentStepInfo] = None) -> None:
        """
        Override step: if AI is disabled, do nothing; otherwise run normal step().
        """
        if not self._agent_enabled:
            return
        await super().step(step_info)

    async def run_interactive(
        self,
        manual_callback: Callable[['InteractiveAgent'], Any],
        max_steps: int = 100,
    ) -> None:
        """
        High-level loop that interleaves manual_callback with AI steps.

        Args:
            manual_callback: a sync or async function called when in manual mode.
            max_steps: maximum number of AI-driven steps to execute.
        """
        for _ in range(max_steps):
            # While manual mode is active, invoke the callback
            while not self._agent_enabled:
                print("🔧 Manual mode active. Invoking manual callback...")
                result = manual_callback(self)
                if asyncio.iscoroutine(result):
                    await result  # allow async manual logic
                await asyncio.sleep(0)
            # Run one AI-driven step
            await self.step()
            # If the last AI step failed, pause for manual takeover
            results = getattr(self.state, 'last_result', None) or []  # list of ActionResult
            errors = [r.error for r in results if getattr(r, 'error', None)]
            if errors:
                print(f"⚠️ Failure detected: {errors}\n" +
                      "Switching to manual mode. Use enable_agent() to resume.")
                self.disable_agent() # must re-enable in fallback

    # Methods for fine-grained interactive control
    async def step_with_prompt(
        self,
        prompt: str,
        step_info: Optional[AgentStepInfo] = None,
    ) -> None:
        """
        Inject a custom prompt as a HumanMessage and execute one agent step.
        Keeping here for now, but do not use.
        Does not maintain agent state well.

        Args:
            prompt: The human prompt to add before stepping.
            step_info: Optional step information for metadata.
        """
        # Add custom prompt to the conversation
        self._message_manager._add_message_with_tokens(HumanMessage(content=prompt))
        # Ensure AI-driven step runs regardless of manual mode
        was_enabled = self._agent_enabled
        self.enable_agent()
        try:
            await super().step(step_info)
        finally:
            # Restore manual mode if it was previously disabled
            if not was_enabled:
                self.disable_agent()

    def add_task(self, new_task: str) -> None:
        """
        Add or update the agent's ultimate task mid-run.

        Args:
            new_task: The new task description.
        """
        # Delegate to the message manager and update task
        self._message_manager.add_new_task(new_task)
        self.task = new_task

    async def get_agent_current_page(self):
        """
        Convenience helper: return the current Playwright page the agent is working with.

        Uses browser_context.get_agent_current_page() if available, else falls back to get_current_page().

        This method is not present in PyPI. Monitor package for updates.
        """
        ctx = self.browser_context
        if hasattr(ctx, 'get_agent_current_page'):
            return await ctx.get_agent_current_page()
        return await ctx.get_current_page()

    async def close(self) -> None:
        """
        Close all resources.
        This method is not present in PyPI. Monitor package for updates.
        """
        import gc
        import logging

        logger = logging.getLogger(__name__)
        try:
            # First close browser resources
            if self.browser_context and not self.injected_browser_context:
                await self.browser_context.close()
            if self.browser and not self.injected_browser:
                await self.browser.close()

            # Force garbage collection
            gc.collect()

        except Exception as e:
            logger.error(f'Error during cleanup: {e}')

    async def run_ai_task(
        self,
        task: str,
        success_condition: Callable[['InteractiveAgent'], bool],
        max_steps: int = 10,
        step_info: Optional[AgentStepInfo] = None
    ) -> bool:
        """
        Let AI complete a specific task fully before returning control.
        Takes in a callback function, runs event loop and returns if task is completed according to callback.
        
        Args:
            task: The task description for the AI
            success_condition: A function that takes the agent and returns True if the task is complete
            max_steps: Maximum number of steps to try completing the task
            step_info: Optional step information for metadata
        
        Returns:
            bool: True if task was completed successfully, False otherwise
        """
        print(f"🤖 AI Task: {task}")
        self.enable_agent()
        self.add_task(task)
        
        # Run steps until task is complete or max steps reached
        for step in range(max_steps):
            await self.step(step_info)
            
            # Check if task is complete
            if await success_condition(self):
                print("✅ AI task completed successfully")
                self.disable_agent()
                return True
                
            # If we hit max steps, task might be incomplete
            if step == max_steps - 1:
                print("⚠️ AI task may be incomplete - hit max steps")
                self.disable_agent()
                return False
        
        self.disable_agent()
        return False

    async def run_single_step(self, task: str, step_info: Optional[AgentStepInfo] = None) -> None:
        """
        Run a single AI step with a specific task.
        This is more reliable than step_with_prompt as it maintains agent state better.
        
        Args:
            task: The task description for the AI
            step_info: Optional step information for metadata
        """
        self.add_task(task)
        await self.step(step_info)

    async def run_until_complete(
        self,
        task: str,
        completion_prompt: str = "Have you completed all the required fields in this section? If yes, respond with 'TASK_COMPLETE'. If no, continue filling out the fields.",
        max_steps: int = 20,
        step_info: Optional[AgentStepInfo] = None
    ) -> bool:
        """
        Let AI run multiple steps until it explicitly confirms completion.
        The AI must respond with 'TASK_COMPLETE' to indicate it's done.
        
        Args:
            task: The task description for the AI
            completion_prompt: The prompt to check if the task is complete
            max_steps: Maximum number of steps to try completing the task
            step_info: Optional step information for metadata
        
        Returns:
            bool: True if task was completed successfully, False otherwise
        """
        print(f"🤖 AI Task: {task}")
        self.enable_agent()
        self.add_task(task)
        
        # Run steps until AI confirms completion or max steps reached
        for step in range(max_steps):
            await self.step(step_info)
            
            # Check if AI has completed the task
            last_message = str(self.state.history.history[-1]) if self.state.history.history else ""
            if "TASK_COMPLETE" in last_message:
                print("✅ AI confirmed task completion")
                self.disable_agent()
                return True
                
            # If we hit max steps, task might be incomplete
            if step == max_steps - 1:
                print("⚠️ AI task may be incomplete - hit max steps")
                self.disable_agent()
                return False
            
            # Add completion check prompt
            self._message_manager._add_message_with_tokens(HumanMessage(content=completion_prompt))
        
        self.disable_agent()
        return False
