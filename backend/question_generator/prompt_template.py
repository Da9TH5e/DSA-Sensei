# question_generator/prompt_template.py

from langchain.prompts import PromptTemplate

question_prompt = PromptTemplate(
    input_variables=["summary"],
    template="""
You are a skilled programming tutor.

Based on the following video summary, do the following:
1. Decide whether the topic is suitable for beginners, intermediate learners, or advanced learners and also you have to choose any one difficulty.
2. Generate up to 3 coding questions appropriate to that difficulty level like if you choose begineer level then all the 3 questions should beginner level only and make variations in them.

Each question must include:
- A clear problem description
- Input format
- Output format
- Example input and output

Summary:
{summary}

Start your response with:
"Deduced Difficulty Level: <Beginner/Intermediate/Advanced>"
Then list the questions.
"""
)
