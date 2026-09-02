import os
from dotenv import load_dotenv
import re
# from google import genai
from groq import Groq

load_dotenv()

# client = genai.Client(
#     api_key=os.environ["GROQ_API_KEY"]
#     # api_key=os.environ["GEMINI_API_KEY"]
# )

client = Groq(
    api_key=os.environ["GROQ_API_KEY"]
)

MODEL = "openai/gpt-oss-20b"


def solve_questions(questions):

    prompt = """
Solve all of the following multiple-choice questions.

For each question, determine the correct option.

Return ONLY a JSON object in this exact format:

{
  "1": "A",
  "2": "C",
  "3": "B"
}

Do not include explanations.

QUESTIONS:
"""

    for i, q in enumerate(questions, 1):
        prompt += f"""

Question {i}:
{q["question"]}

A: {q["options"]["A"]}
B: {q["options"]["B"]}
C: {q["options"]["C"]}
D: {q["options"]["D"]}
"""

    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],
        reasoning_effort="low",
        max_completion_tokens=300,
        temperature=0
    )

    content = response.choices[0].message.content or ""

    print("\nRaw model output:")
    print(content)

    # Extract JSON from response
    match = re.search(r"\{.*\}", content, re.DOTALL)

    if not match:
        raise ValueError(
            f"Could not find JSON in model response:\n{content}"
        )

    import json

    answers = json.loads(match.group(0))

    # Validate every answer
    result = {}

    for i in range(1, len(questions) + 1):

        answer = answers.get(str(i), "").strip().upper()

        if answer not in ("A", "B", "C", "D"):
            raise ValueError(
                f"Invalid answer for question {i}: {answer}"
            )

        result[i] = answer

    return result


#v1 working fine
# def solve_question(question, options):

#     prompt = f"""
# Solve this multiple-choice question.

# Question:
# {question}

# A: {options["A"]}
# B: {options["B"]}
# C: {options["C"]}
# D: {options["D"]}

# Return ONLY the correct letter: A, B, C, or D.
# """

#     response = client.chat.completions.create(
#         model=MODEL,
#         messages=[
#             {
#                 "role": "user",
#                 "content": prompt
#             }
#         ],
#         reasoning_effort="low",
#         max_completion_tokens=100
#     )

#     content = response.choices[0].message.content or ""

#     print("Raw model output:", repr(content))

#     match = re.search(r"\b([ABCD])\b", content.upper())

#     if match:
#         return match.group(1)

#     raise ValueError(
#         f"Could not determine answer. Raw output: {content!r}"
#     )


# def solve_question(question, options):

#     prompt = f"""
# Answer this multiple-choice question.

# Question:
# {question}

# Options:
# A: {options["A"]}
# B: {options["B"]}
# C: {options["C"]}
# D: {options["D"]}

# Return ONLY the single letter of the correct answer:
# A, B, C, or D.
# """

#     response = client.models.generate_content(
#         model="gemini-3.6-flash",
#         contents=prompt
#     )

#     answer = response.text.strip().upper()

#     if answer not in ["A", "B", "C", "D"]:
#         raise ValueError(f"Invalid AI answer: {answer}")

#     return answer
