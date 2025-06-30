import os
from openrouter import Client
from schemas import Clarification # Assuming schemas.py is in the parent directory or PYTHONPATH is set

# Attempt to load environment variables if python-dotenv is present
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass # python-dotenv not installed, environment variables should be set manually

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
# Recommended model, but can be changed.
# To see available models, run: `openrouter models` in your terminal
# Or visit https://openrouter.ai/models
OPENROUTER_MODEL = os.getenv("OPENROUTER_CLARIFIER_MODEL", "mistralai/mistral-7b-instruct:free")


class ClarifierAgent:
    def __init__(self, api_key: str = None, model: str = None):
        self.api_key = api_key or OPENROUTER_API_KEY
        if not self.api_key:
            raise ValueError("OpenRouter API key not provided. Set OPENROUTER_API_KEY environment variable.")
        self.client = Client(api_key=self.api_key)
        self.model = model or OPENROUTER_MODEL
        if not self.model:
            # Default to a known free model if not set
            self.model = "mistralai/mistral-7b-instruct:free"


    def ask_question(self, user_input: str, project_context: str = "") -> Clarification:
        """
        Generates a clarifying question based on user input using an LLM.
        """
        prompt = f"""The user has stated a goal or idea: "{user_input}".
Project context: {project_context if project_context else "General"}

You are a helpful AI assistant. Your task is to ask a single, concise clarifying question to better understand the user's intention or to help them elaborate on a specific aspect of their goal.
The question should encourage the user to provide more details, consider edge cases, or define scope.
Do not offer solutions or make assumptions. Just ask one clear question.
For example, if the user says 'I want to build a new app', a good question might be 'What is the primary problem this new app aims to solve for its users?'
If the user says 'Improve website performance', a good question might be 'Which specific aspects of website performance are you looking to improve (e.g., loading speed, responsiveness, resource usage)?'

Generate only the question text.
"""
        question_text = f"Could you tell me more about '{user_input}'?" # Default fallback

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an AI assistant that asks clarifying questions to help users elaborate on their project goals or ideas. Respond with only the question text."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=100, # Max length of the generated question
                temperature=0.7 # A bit of creativity
            )
            if response.choices and response.choices[0].message.content:
                question_text = response.choices[0].message.content.strip()
            else:
                print(f"Warning: LLM returned no content for ClarifierAgent. Falling back to default. Response: {response}")

        except Exception as e:
            print(f"Error calling OpenRouter API in ClarifierAgent: {e}")
            # Fallback to a simpler question if API call fails
            if "plan" in user_input.lower() or "goal" in user_input.lower():
                question_text = f"Can you provide more specific details about your goal: '{user_input}'? For example, what are the key objectives or desired outcomes?"
            elif "problem" in user_input.lower() or "issue" in user_input.lower():
                question_text = f"Could you elaborate on the problem: '{user_input}'? What are the main challenges you're facing?"
            else:
                question_text = f"What specific aspect of '{user_input}' would you like to explore further or get help with?"


        clarification = Clarification(
            question=question_text,
            context=project_context if project_context else user_input
        )
        return clarification

    def process_user_response(self, clarification: Clarification, user_answer: str) -> Clarification:
        """
        Processes the user's answer to a clarification question.
        """
        clarification.answer = user_answer
        # Potentially, further processing or storage could happen here.
        return clarification

if __name__ == "__main__":
    # Example Usage (Requires OPENROUTER_API_KEY to be set in .env or environment)
    print(f"Attempting to use model: {OPENROUTER_MODEL}")
    if not OPENROUTER_API_KEY:
        print("OPENROUTER_API_KEY not set. Please set it in your environment or a .env file to run this example.")
        print("Example: OPENROUTER_API_KEY='your_api_key_here'")
        exit()

    agent = ClarifierAgent()

    queries = [
        "I want to build a new app.",
        "My project is facing a major roadblock with the database.",
        "Need ideas for a marketing campaign for a SaaS product.",
        "Develop a system for real-time data processing.",
        "Refactor the user authentication module."
    ]

    for user_query in queries:
        print(f"\nUser Query: {user_query}")
        q = agent.ask_question(user_query, project_context="Test Project Alpha")
        print(f"Agent Question: {q.question}")
        # Simulate user answering (optional here)
        # user_ans = "Some detailed answer..."
        # q = agent.process_user_response(q, user_ans)
        # print(f"User Answer: {q.answer}")
        print("-" * 30)
