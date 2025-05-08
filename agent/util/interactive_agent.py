"""
interactive_agent.py

Subclass of Agent that supports switching between manual and AI-driven control.
"""
import asyncio
from typing import Callable, Any, Optional

from browser_use.agent.service import Agent, AgentStepInfo


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

    async def close(self) -> None:
        """
        Close all resources.
        This method is not present in . Monitor repo for updates.
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
