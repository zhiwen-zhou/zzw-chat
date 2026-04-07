import os
import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("DASHSCOPE_API_KEY")
URL = "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions"

def chat_completion(messages, model="deepseek-r1"):
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": model,
        "messages": messages,
        "temperature": 0.2
    }

    response = requests.post(URL, headers=headers, json=payload)
    response.raise_for_status()
    return response.json()["choices"][0]["message"]["content"]