import praw
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