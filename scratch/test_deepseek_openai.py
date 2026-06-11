import os
import openai
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("DEEPSEEK_API_KEY")
print(f"API Key: {api_key[:10]}...")

client = openai.OpenAI(
    api_key=api_key,
    base_url="https://api.deepseek.com"
)

try:
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {"role": "user", "content": "Merhaba, bu bir test mesajıdır. Lütfen sadece 'Merhaba' yaz."}
        ]
    )
    print("Success!")
    print(response.choices[0].message.content)
except Exception as e:
    print(f"Failed: {e}")
