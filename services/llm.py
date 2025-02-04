from openai import OpenAI
import os

def create_content(prompt):
    messages=[
            {"role": "user", "content": prompt},
    ]

    response = call_llm(messages)

    if not response:
        response = call_llm(messages, "Secondary")

    return response


def call_llm(messages, model_type="Primary", retries=3):
    if model_type == "Primary":
        client = OpenAI(api_key=os.getenv("LLM_API_KEY"), base_url=os.getenv("BASE_URL", "https://api.openai.com/v1"))
        model = os.getenv("LLM_MODEL", "o1-preview")
    else:
        client = OpenAI(api_key=os.getenv("SECONDARY_LLM_API_KEY"), base_url=os.getenv("SECONDARY_BASE_URL", "https://api.openai.com/v1"))
        model = os.getenv("SECONDARY_LLM_MODEL", "o1-preview")

    for attempt in range(retries):
        try: 
            response = client.chat.completions.create(
                model=model,
                messages=messages,
                stream=False
            )

            return response.choices[0].message.content
        except ValueError:
            print(f"Attempt#{attempt+1} | {model} Model : Failed to generate content")
