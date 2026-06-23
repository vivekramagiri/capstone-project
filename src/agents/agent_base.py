"""
Base agent implementation using Anthropic SDK with tool use
"""

from typing import Any, Callable, Optional, List, Dict
from anthropic import Anthropic
from anthropic.types.tool_param import ToolParam
from src.config import settings
from src.utils.logger import get_logger

logger = get_logger(__name__)


class BaseAgent:
    def __init__(self, name: str, system_prompt: str):
        self.name = name
        self.system_prompt = system_prompt
        self.client = Anthropic(api_key=settings.ANTHROPIC_API_KEY, base_url=settings.ANTHROPIC_API_URL)
        self.tools: List[ToolParam] = []
        self.tool_functions: Dict[str, Callable] = {}

    def add_tool(self, tool_definition: ToolParam, tool_function: Callable) -> None:
        """Register a tool that the agent can use"""
        self.tools.append(tool_definition)
        self.tool_functions[tool_definition["name"]] = tool_function

    def execute_tool(self, tool_name: str, tool_input: dict) -> Any:
        """Execute a registered tool"""
        if tool_name not in self.tool_functions:
            return {"error": f"Tool '{tool_name}' not found"}

        try:
            result = self.tool_functions[tool_name](**tool_input)
            logger.info(f"Agent {self.name} executed tool {tool_name}")
            return result
        except Exception as e:
            logger.error(f"Error executing tool {tool_name}: {str(e)}")
            return {"error": f"Tool execution failed: {str(e)}"}

    def run(self, user_message: str, max_iterations: int = 10) -> dict:
        """
        Run the agent with an agentic loop (tool use until completion)

        Args:
            user_message: The user input/task for the agent
            max_iterations: Maximum tool use iterations to prevent infinite loops

        Returns:
            Final response from the agent
        """
        messages = [{"role": "user", "content": user_message}]
        iteration = 0

        logger.info(f"Agent {self.name} starting with message: {user_message[:100]}")

        while iteration < max_iterations:
            iteration += 1

            response = self.client.messages.create(
                model=settings.LLM_MODEL,
                max_tokens=settings.LLM_MAX_TOKENS,
                system=self.system_prompt,
                tools=self.tools if self.tools else None,
                messages=messages,
            )

            # Add assistant response to messages
            messages.append({"role": "assistant", "content": response.content})

            # Check if we're done (no more tool use)
            if response.stop_reason == "end_turn":
                # Extract text response
                for block in response.content:
                    if hasattr(block, "text"):
                        logger.info(f"Agent {self.name} completed with response")
                        return {
                            "success": True,
                            "response": block.text,
                            "iterations": iteration,
                        }
                return {
                    "success": False,
                    "error": "No text response from model",
                    "iterations": iteration,
                }

            # Handle tool use
            if response.stop_reason == "tool_use":
                tool_results = []
                for block in response.content:
                    if block.type == "tool_use":
                        logger.info(f"Agent {self.name} calling tool: {block.name}")
                        result = self.execute_tool(block.name, block.input)
                        tool_results.append(
                            {
                                "type": "tool_result",
                                "tool_use_id": block.id,
                                "content": str(result),
                            }
                        )

                # Add tool results to messages
                messages.append({"role": "user", "content": tool_results})
            else:
                # Unknown stop reason
                logger.warning(f"Unexpected stop reason: {response.stop_reason}")
                break

        return {
            "success": False,
            "error": f"Max iterations ({max_iterations}) reached",
            "iterations": iteration,
        }
