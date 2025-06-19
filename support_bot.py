import discord
import openai
import os
from dotenv import load_dotenv
from discord.ext import commands

load_dotenv()
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
openai.api_key = OPENAI_API_KEY

# Intents
intents = discord.Intents.default()

# Create the bot instance
bot = commands.Bot(command_prefix="!", intents=intents)

SYSTEM_PROMPT = """
You are a helpful, friendly support assistant for Neuron. You assist users with common issues, setup, and troubleshooting. Use mainly the provided knowledge. You understand discord.

Learn about these websites — you are a Neuron support bot. One of Neuron's products is 4DSKY:
https://www.neuron.world/
https://docs.neuron.world/
https://4dsky.com/
https://docs.4dsky.com/
"""

@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f"✅ Bot connected as {bot.user}")

@bot.tree.command(name="ask", description="Ask the Neuron support bot a question.")
async def ask(interaction: discord.Interaction, question: str):
    await interaction.response.defer(thinking=True)

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",  # or gpt-3.5-turbo
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": question}
            ],
            temperature=0.5,
            max_tokens=500
        )
        answer = response.choices[0].message["content"]
        await interaction.followup.send(answer)

    except Exception as e:
        await interaction.followup.send(f"❌ Something went wrong: {e}")

bot.run(DISCORD_TOKEN)
