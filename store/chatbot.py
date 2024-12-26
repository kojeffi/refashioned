import openai
import os

# Set your OpenAI API key from environment variable
api_key = os.getenv('OPENAI_API_KEY')
openai.api_key = api_key

def support_chatbot(user_query):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",  # Or "gpt-4" if you have access to it
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": user_query}
        ],
        max_tokens=150
    )
    return response.choices[0].message['content'].strip()
