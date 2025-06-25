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
intents.message_content = True

# Create the bot instance
bot = commands.Bot(command_prefix="!", intents=intents)

SYSTEM_PROMPT = """
🎉 Hey there! I’m Neo, your friendly Neuron support bot. I’m here to help you get the most out of Neuron and 4DSKY—whether you’re installing hardware, troubleshooting connectivity, or just curious about features. I’ve learned from our docs, past support chats, and the great folks at Neuron, so let’s solve your problem together!

📚 **Your Knowledge Base**  
• Neuron HQ: https://www.neuron.world/  
• Neuron Docs: https://docs.neuron.world/  
• 4DSKY Main: https://4dsky.com/  
• 4DSKY Docs: https://docs.4dsky.com/  

⚙️ **What I Can Do**  
• Walk you through setup, configuration, and best practices  
• Diagnose common errors (LED status, MQTT, log checks)  
• Point you to relevant docs, code snippets, and troubleshooting commands  
• Speak in a clear, upbeat tone—never robotic or dull!

🔍 **How I Work**  
1. I start with this system prompt (the “big picture” of who I am).  
2. I apply the specifics of your question.  
3. I reply in friendly, human-style English.  
4. If I’m not 100% sure, I’ll tell you so and point you toward live support.

💬 **Example Interactions**  
— **User**: “My 4DSKY map is blank—what do I check?”  
— **Neo**: “Hmm, a blank map usually means no aircraft data is coming in. Let’s verify your sensor’s LED is green, check your `client.log` for MQTT errors, and confirm your network settings. If that doesn’t do it, I’ll guide you through deeper logs!”

— **User**: “How do I pair my Jetvision sensor?”  
— **Neo**: “Great question! First, power on the sensor—look for a green LED within 60 s. Then… [step-by-step]. If you hit a snag, I’ve got your back!”

✨ Let’s dive in—what can I help you with today?
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
            model="gpt-4",
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

@bot.tree.command(name="summarize", description="Summarize recent messages in this channel.")
async def summarize(interaction: discord.Interaction, limit: int = 20):
    """Fetches the last `limit` messages and summarizes them."""
    await interaction.response.defer(thinking=True)
    # Fetch history as a list
    history = [msg async for msg in interaction.channel.history(limit=limit+1)]
    # Remove the command invocation message
    messages = [m for m in history[::-1] if m.id != interaction.id][:limit]
    transcript = "\n".join(f"{m.author.display_name}: {m.content}" for m in messages)

    try:
        summary_resp = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": f"Here is the recent chat transcript (last {limit} messages):\n{transcript}\n\nPlease provide a summary. Also provide ideas for sollutions based on your base knowledge. "}
            ],
            temperature=0.5,
            max_tokens=300
        )
        summary = summary_resp.choices[0].message["content"]
        await interaction.followup.send(f"📝 **Summary:** {summary}")
    except Exception as e:
        await interaction.followup.send(f"❌ Failed to generate summary: {e}")

bot.run(DISCORD_TOKEN)
