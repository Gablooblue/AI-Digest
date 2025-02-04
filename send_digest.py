from datetime import datetime as dt
from dotenv import load_dotenv
from bs4 import BeautifulSoup
import re
import logging

from services.mailers import send_daily_newsletter
from services.llm import create_content
from services.reddit import pull_posts

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def build_prompt(posts, date):

    context_prompt = "You are a top tech and AI email newsletter writer. You will copy the styles of other popular email newsletters like Morning Brew, Proof of Intel, e27 Daily Digest. You will be given a list of top posts of the day from the subreddit r/LocalLLaMa, a subreddit dedicated to news about new LLM and AI advancements. You will read and understand all the top posts from the day and return a quick summary headline and subheader that encompasses the entire day's stories. Then build 3-5 stories that dive deeper into each topic that is brought up. Focus on providing a factual and unbiased point of view and try to mimic the voice of a news reporter. The output should be formatted with html. Style the email output using gmail-friendly HTML. Do not put it within a code block (```html ```).\n\nHere is the data for today:\n\n"

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

def get_subject(html_content, date):
    soup = BeautifulSoup(html_content, "html.parser")

    h1_tag = soup.find("h1")

    if h1_tag:
        return h1_tag.get_text()
    else:
        return f"Gab's Daily AI Digest - {date}"

    return None

def get_body(html_content):
    soup = BeautifulSoup(html_content, "html.parser")

    body_tag = soup.find("body")

    if body_tag:
        return body_tag.get_text()
    else:
        return html_content

    return None

def remove_code_fences(text):
    """
    Finds ```<lang> ... ``` blocks and replaces them
    with just the content inside (strips backticks and optional lang).
    """
    # Regex explanation:
    #   ```      matches the opening triple backticks
    #   [a-zA-Z]*  optionally capture a language label (like 'html')
    #   (.*?)    capture everything (non-greedy) until
    #   ```      the closing triple backticks
    # DOTALL so '.' matches newlines as well
    pattern = r"```[a-zA-Z]*\n(.*?)\n```"
    return re.sub(pattern, r"\1", text, flags=re.DOTALL)

def main():
    load_dotenv()

    date = dt.now().strftime("%b %d %Y")

    posts = pull_posts()

    prompt = build_prompt(posts, date)

    body_content = create_content(prompt)
    body_content = remove_code_fences(body_content)
    #body_content = get_body(body_content)

    content = {}
    logging.info("Building content")
    content["body"] = body_content
    content["subject"] = get_subject(content["body"], date)
    logging.info(content)

    logging.info("Sending emails")
    send_daily_newsletter(content)

    logging.info('Finished')

main()
