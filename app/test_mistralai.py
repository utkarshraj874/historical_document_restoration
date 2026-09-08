import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq

load_dotenv()

llm = ChatGroq(
    model="openai/gpt-oss-120b",   # or another Groq-supported model
    groq_api_key=os.getenv("GROQCLOUD_API_KEY")
)

prompt = """Correct the following text:

1. "Histry 0f inda"
2. "indi is sovrgn naton"
"""

response = llm.invoke(prompt)
print(response.content)
