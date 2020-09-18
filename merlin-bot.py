import discord
import numpy as np
import asyncio
from mods import Status

# Init Discord
client = discord.Client()

# Init Content Query
status = Status()

print("Listening...")

@client.event
async def on_message(msg):
    # Get message
    msg.content = msg.content.lower()

    if msg.author == client.user:
        return

    # ===== STATUS =====
    if msg.content.startswith("query") or msg.content.startswith("q"):
        response = status.query(msg.content)
        print(response)
        await msg.channel.send(response)
        
    elif msg.content.startswith("add") or msg.content.startswith("a"):
        response = status.add(msg.content)
        print(response)
        await msg.channel.send(response)
        
    elif msg.content.startswith("update") or msg.content.startswith("u"):
        response = status.update(msg.content)
        print(response)
        await msg.channel.send(response)
        
    # ===== FUNNEL =====
    elif msg.content.startswith("remind"):
        time = msg.content.split()[1]
        await msg.channel.send(f"Reminder set for {time} seconds")
        
        await asyncio.sleep(int(time))
        
        await msg.channel.send("Time elapsed")
        
        
    

client.run('NzQ4NDUxMjk0OTIyMTQ1ODEz.X0dnlg.dpUItPEVNDflzXXHJhhcPEvVufU')