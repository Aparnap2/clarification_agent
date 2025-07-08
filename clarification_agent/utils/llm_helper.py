import os
from typing import List, Dict, Any
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

# Load environment variables
load_dotenv()

class LLMHelper:
    """A streamlined helper class for interacting with language models."""

    def __init__(self, model_name: str = "moonshotai/kimi-dev-72b:free"):
        """Initializes the LLM helper with a specified model."""
        self.llm = ChatOpenAI(
           base_url="https://openrouter.ai/api/v1",
            model=model_name,
            api_key=os.getenv("OPENAI_API_KEY"),
            temperature=0.7,
        )

    def generate(self, prompt: str) -> str:
        """
        Generates a response for a single prompt.

        Args:
            prompt: The user's prompt.

        Returns:
            The language model's response.
        """
        messages = [HumanMessage(content=prompt)]
        response = self.llm.invoke(messages)
        return response.content

    def generate_with_history(
        self, prompt: str, history: List[Dict[str, Any]]
    ) -> str:
        """
        Generates a response, considering the conversation history.

        Args:
            prompt: The system or initial user prompt.
            history: A list of previous messages in the conversation.

        Returns:
            The language model's response.
        """
        messages = [SystemMessage(content=prompt)]
        for message in history:
            if message.type == "human":
                messages.append(HumanMessage(content=message.content))
            elif message.type == "ai":
                messages.append(AIMessage(content=message.content))
        
        response = self.llm.invoke(messages)
        return response.content