import os
import requests
import discord
from discord.ext import tasks, commands
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
DISCORD_CHANNEL_ID = int(os.getenv('DISCORD_CHANNEL_ID'))
TWITTER_BEARER_TOKEN = os.getenv('TWITTER_BEARER_TOKEN')
REDDIT_CLIENT_ID = os.getenv('REDDIT_CLIENT_ID')
REDDIT_SECRET = os.getenv('REDDIT_SECRET')
REDDIT_USERNAME = os.getenv('REDDIT_USERNAME')
REDDIT_PASSWORD = os.getenv('REDDIT_PASSWORD')
TWITTER_USER_ID = os.getenv('TWITTER_USER_ID')
REDDIT_SUBREDDIT = os.getenv('REDDIT_SUBREDDIT')

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')
    twitter_feed.start()
    reddit_feed.start()

# Twitter API request headers
twitter_headers = {
    "Authorization": f"Bearer {TWITTER_BEARER_TOKEN}"
}

@tasks.loop(minutes=5)
async def twitter_feed():
    """
    Fetches recent tweets from a specific Twitter user and sends updates to Discord.
    """
    url = f"https://api.twitter.com/2/users/{TWITTER_USER_ID}/tweets"
    response = requests.get(url, headers=twitter_headers)

    if response.status_code == 200:
        tweets = response.json().get("data", [])
        for tweet in tweets[:5]:  # Process the latest 5 tweets
            tweet_content = tweet.get("text")
            tweet_id = tweet.get("id")
            tweet_url = f"https://twitter.com/i/web/status/{tweet_id}"

            channel = bot.get_channel(DISCORD_CHANNEL_ID)
            if channel:
                await channel.send(f"**New Tweet:** {tweet_content}\n{tweet_url}")
    else:
        print(f"Error fetching tweets: {response.status_code}")

@tasks.loop(minutes=5)
async def reddit_feed():
    """
    Fetches recent posts from a subreddit and sends updates to Discord.
    """
    url = f"https://www.reddit.com/r/{REDDIT_SUBREDDIT}/new.json"
    headers = {"User-Agent": "discord-bot"}
    auth = requests.auth.HTTPBasicAuth(REDDIT_CLIENT_ID, REDDIT_SECRET)
    data = {"grant_type": "password", "username": REDDIT_USERNAME, "password": REDDIT_PASSWORD}
    token_response = requests.post("https://www.reddit.com/api/v1/access_token", auth=auth, data=data, headers=headers)
    token = token_response.json().get("access_token")

    headers["Authorization"] = f"bearer {token}"
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        posts = response.json().get("data", {}).get("children", [])
        for post in posts[:5]:  # Process the latest 5 posts
            post_data = post.get("data")
            post_title = post_data.get("title")
            post_url = f"https://www.reddit.com{post_data.get('permalink')}"

            channel = bot.get_channel(DISCORD_CHANNEL_ID)
            if channel:
                await channel.send(f"**New Reddit Post:** {post_title}\n{post_url}")
    else:
        print(f"Error fetching Reddit posts: {response.status_code}")

bot.run(DISCORD_TOKEN)
