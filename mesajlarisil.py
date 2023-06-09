import discord
import asyncio

TOKEN = ""
YOUR_CHANNEL_ID =   # Silmek istediğiniz kanalın ID'sini buraya girin

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)


@client.event
async def on_ready():
    print(f"We have logged in as {client.user}")


@client.event
async def on_message(message):
    if message.channel.id == YOUR_CHANNEL_ID:
        await asyncio.sleep(3)  # Wait for 3 seconds
        await message.delete()


client.run(TOKEN)
