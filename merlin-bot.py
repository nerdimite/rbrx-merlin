import discord
import numpy as np
import asyncio
from mods import Status, Funnel

# Init Discord
client = discord.Client()

# Init Status Mod
status = Status()

# Init Funnel Mod
funnel = Funnel()

print("Listening...")

@client.event
async def on_message(msg):
    # Get message
    msg.content = msg.content.lower()

    if msg.author == client.user:
        return
    
    if msg.content.startswith('mh'):
        await msg.channel.send(f"Hello {msg.author.mention}!")

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
    elif msg.content.startswith("remind") or msg.content.startswith("r"):
        
        t_delta, args = funnel.remind(msg.content)
        
        if t_delta != -1:
            await msg.channel.send(f"Will remind you to \"{args['msg']}\" at {args['time']}")

            print(t_delta)
            await asyncio.sleep(int(t_delta))

            await msg.channel.send(f"**Reminder:** {args['msg']}")
        else:
            await msg.channel.send(args)
            
            
client.run('NzQ4NDUxMjk0OTIyMTQ1ODEz.X0dnlg.dpUItPEVNDflzXXHJhhcPEvVufU')