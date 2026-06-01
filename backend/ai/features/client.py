import os
import openai
from dotenv import load_dotenv

load_dotenv()

# Configure OpenAI client for OpenRouter
client = openai.OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv('OPENROUTER_API_KEY', os.getenv('OPENAI_API_KEY')),
)

MODEL_NAME = "meta-llama/llama-3-8b-instruct"

AGENT_SYSTEM_PROMPT = """You are an AI inventory management agent with the following capabilities:
1. Analyze inventory patterns and predict demand
2. Suggest optimal stock levels based on historical data
3. Identify potential stockouts and overstock situations
4. Provide recommendations for inventory optimization
5. Generate detailed reports on inventory performance
Use the provided data context to answer queries accurately."""
