import openai
import anthropic
import deepseek
import time
import threading
import os
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY')
DEEPSEEK_API_KEY = os.getenv('DEEPSEEK_API_KEY')

# Initialize API clients
openai.api_key = OPENAI_API_KEY
anthropic_client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
deepseek.api_key = DEEPSEEK_API_KEY

def getAIResponse(api_choice, context, user_input):
    if api_choice == "OpenAI":
        client = openai.OpenAI(api_key=OPENAI_API_KEY)
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "This is the conversation history:"},
                {"role": "system", "content": context},
                {"role": "user", "content": user_input}
            ]
        )
        bot_response = response.choices[0].message.content
    elif api_choice == "Claude":
        prompt = f"This is the conversation history:\n{context}\n\nHuman: {user_input}\n\nAssistant:"
        response = anthropic_client.completions.create(
            model="claude-2",
            max_tokens_to_sample=1000,
            prompt=prompt,
            stop_sequences=["\n\nHuman:"]
        )
        bot_response = response.completion
    elif api_choice == "DeepSeek":
        prompt = f"This is the conversation history:\n{context}\n\nHuman: {user_input}\n\nAI:"
        response = deepseek.generate(
            prompt=prompt,
            model="deepseek-7b",
            max_tokens=1000
        )
        bot_response = response['choices'][0]['text']
        
    return bot_response
    