# question_generator/generator.py

import os
from dotenv import load_dotenv
from langchain_core.runnables import RunnableSequence
from langchain_groq import ChatGroq
from .prompt_template import question_prompt

load_dotenv()

groq_api_key = os.getenv("GROQ_API_KEY")
if not groq_api_key:
    raise EnvironmentError("GROQ_API_KEY not set in environment.")

model_name = os.getenv("GROQ_MODEL_NAME", "llama3-8b-8192")  # Updated to supported model

llm = ChatGroq(model_name=model_name, api_key=groq_api_key, temperature=0.7)

chain = RunnableSequence(question_prompt | llm)

def generate_questions(summary: str) -> str:
    return chain.invoke({"summary": summary}).content