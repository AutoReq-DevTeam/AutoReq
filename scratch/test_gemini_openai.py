import os
import openai
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
print(f"API Key: {api_key[:10]}...")

client = openai.OpenAI(
    api_key=api_key,
    base_url="https://generativelanguage.googleapis.com/v1beta/"
)

try:
    response = client.chat.completions.create(
        model="gemini-2.5-flash",
        messages=[
            {"role": "user", "content": "Merhaba, bu bir test mesajıdır. Lütfen sadece 'Merhaba' yaz."}
        ]
    )
    print("Success!")
    print(response.choices[0].message.content)
except Exception as e:
    print(f"Failed: {e}")
