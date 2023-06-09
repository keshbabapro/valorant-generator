import discord
import random
import asyncio
import time

TOKEN = ""
ACCOUNTS_FILE_PREFIX = "accounts"
NUM_PARTS = 1
COMMAND_COOLDOWN = 3600  # Komutun bir saat boyunca kullanılamayacağı süre (saniye cinsinden)
MAX_RECIPIENTS = 99
PREFIX = "."

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)
last_command_time = {}
used_accounts = {}
log_channel_id =   # Log kanalının ID'sini buraya girin
allowed_channel_id =   # İzin verilen kanalın ID'sini buraya girin

def get_random_accounts():
    random_part_numbers = random.sample(range(1, NUM_PARTS + 1), NUM_PARTS)
    craftrise_accounts = []

    for part_number in random_part_numbers:
        part_filename = f"{ACCOUNTS_FILE_PREFIX}{part_number}.txt"
        with open(part_filename, "r", encoding="utf-8") as file:
            accounts = file.read().replace('"', '').splitlines()
            craftrise_accounts.extend(accounts)

    return craftrise_accounts

@client.event
async def on_ready():
    print(f"We have logged in as {client.user}")

@client.event
async def on_message(message):
    if message.author == client.user:
        return
    
    if not message.content.startswith(PREFIX):
        return
    
    if message.channel.id != allowed_channel_id:
        await message.channel.send("Bu komut sadece belirli bir kanalda kullanılabilir.")
        return
    
    command = message.content[len(PREFIX):].strip()
    
    if command == "craftrise":
        current_time = time.time()
        last_time = last_command_time.get(message.author.id, 0)
        
        if current_time - last_time < COMMAND_COOLDOWN:
            remaining_time = COMMAND_COOLDOWN - (current_time - last_time)
            await message.channel.send(f"{message.author.mention}, komutu tekrar kullanmak için {int(remaining_time):.0f} saniye beklemelisiniz.")
            return
        
        last_command_time[message.author.id] = current_time
        
        craftrise_accounts = get_random_accounts()
        
        if craftrise_accounts:
            if len(used_accounts) >= MAX_RECIPIENTS:
                used_accounts.pop(list(used_accounts.keys())[0])  # İlk kullanılan hesabı sil
            
            available_accounts = [account for account in craftrise_accounts if account not in used_accounts.values()]
            
            if not available_accounts:
                await message.channel.send("Üzgünüz, tüm Valorant hesapları kullanılmış durumda.")
                return
            
            random_account = random.choice(available_accounts)
            used_accounts[message.author.id] = random_account
            
            guild = message.guild
            overwrites = {
                guild.default_role: discord.PermissionOverwrite(read_messages=False),
                message.author: discord.PermissionOverwrite(read_messages=True)
            }
            channel = await guild.create_text_channel(name="valorant-hesaplari", overwrites=overwrites)
            
            log_channel = client.get_channel(log_channel_id)
            if log_channel:
                log_message = f"Hesabı alan kişi: {message.author.name}#{message.author.discriminator}\nHesap: {random_account}"
                await log_channel.send(log_message)
            
            await message.channel.send(f"{message.author.mention}, rastgele Valorant hesabı sadece sizin için bir süreliğine paylaşıldı: {channel.mention}")
            
            await channel.send(f"Rastgele Valorant hesabı sadece sizin için bir süreliğine paylaşıldı. İşte hesap bilgileri:\nHesap: {random_account}")
            
            def check_channel(ch):
                return ch.id == channel.id
            
            try:
                await client.wait_for("channel_delete", check=check_channel, timeout=120)  # 2 dakika boyunca kanal silinmesini bekleyin
            except asyncio.TimeoutError:
                pass
            
            if channel:
                await channel.delete()
        else:
            await message.channel.send("Üzgünüz, şu anda mevcut bir Craftrise hesabı bulunmamaktadır.")

client.run(TOKEN)
