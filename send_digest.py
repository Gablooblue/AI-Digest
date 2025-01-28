from openai import OpenAI
import praw
from datetime import datetime as dt
from dotenv import load_dotenv
import requests
import os

def pull_posts():
    reddit = praw.Reddit(
            client_id=os.getenv("CLIENT_ID"),
            client_secret=os.getenv("CLIENT_SECRET"),
            user_agent=os.getenv("USER_AGENT")
            )

    posts = reddit.subreddit("LocalLLaMA").top(limit=100, time_filter="day")
    filtered_posts = [p for p in posts if not p.stickied and p.selftext != "" and p.score > 30]

    return filtered_posts

def build_prompt(posts, date):

    context_prompt = "You are a top tech and AI email newsletter writer. You will copy the styles of other popular email newsletters like Morning Brew, Proof of Intel, e27 Daily Digest. You will be given a list of top posts of the day from the subreddit r/LocalLLaMa, a subreddit dedicated to news about new LLM and AI advancements. You will read and understand all the top posts from the day and return a quick summary headline and subheader that encompasses the entire day's stories. Then build 3-5 stories that dive deeper into each topic that is brought up. Focus on providing a factual and unbiased point of view and try to mimic the voice of a news reporter. Style the email output using gmail-friendly HTML. Do not put it within a code block (```html ```).\n\nHere is the data for today:\n\n"

    prompt = f"Top Posts on r/LocalLLaMa for {date}\n"
    prompt += "Posts are sorted in descending order\n"
    for post in posts:
        prompt += "-----------------\n"
        prompt += f"Title: {post.title}\n"
        prompt += f"Total Score: {post.score}\n"
        prompt += "-- START OF POST CONTENT -- \n"
        prompt += post.selftext + "\n"
        prompt += "-- END OF POST CONTENT -- \n"

    full_prompt = context_prompt + prompt

    return full_prompt

def create_content(prompt):
    #client = OpenAI(api_key=DEEPSEEK_API_KEY, base_url="https://api.deepseek.com")
    client = OpenAI(api_key=os.getenv("LLM_API_KEY"), base_url=os.getenv("BASE_URL", "https://api.openai.com/v1"))

    response = client.chat.completions.create(
        model="o1-preview",
        messages=[
                {"role": "user", "content": prompt},
            ],
        stream=False
    )

    return response.choices[0].message.content

def send_email(content, date):
    url = "https://app.loops.so/api/v1/transactional"

    payload = {
        "email": "gabrielhenry.lopez@gmail.com",
        "transactionalId": os.getenv('LOOPS_TRANSACTIONAL_ID'),
        "addToAudience": True,
        "dataVariables": {
            "content": content,
            "date": date
        },
    }
    headers = {
        "Authorization": f"Bearer {os.getenv('LOOPS_API_KEY')}",
        "Content-Type": "application/json"
    }

    response = requests.request("POST", url, json=payload, headers=headers)

    print(response)

def main():
    load_dotenv()

    date = dt.now().strftime("%b %d %Y")

    posts = pull_posts()

    prompt = build_prompt(posts, date)

    print("Building content")
    content = create_content(prompt)
    print(content)

    print("Sending emails")
    send_email(content, date)

    print('finished')

main()
