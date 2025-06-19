import discord
import openai
import os
from dotenv import load_dotenv

load_dotenv()
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

intents = discord.Intents.default()
intents.messages = True
intents.message_content = True
client = discord.Client(intents=intents)

openai.api_key = openai.api_key = os.getenv("OPENAI_API_KEY")

SYSTEM_PROMPT = """
You are a helpful, friendly support assistant for MyProduct. You assist users with common issues, setup, and troubleshooting. Use only the provided knowledge. You understand discord. 

learn about these websites - you are a Neuron support bot, one of neurons product is 4dsky
https://www.neuron.world/
https://docs.neuron.world/
https://4dsky.com/
https://docs.4dsky.com/


"""

@client.event
async def on_ready():
    print(f'🤖 Bot connected as {client.user}')

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    user_input = message.content

    response = openai.ChatCompletion.create(
        model="gpt-4",  # use gpt-3.5-turbo if needed
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_input}
        ]
    )

    reply = response.choices[0].message.content
    await message.channel.send(reply)

client.run(DISCORD_TOKEN)
