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
async def on_message(ctx):
    # Get message
#     ctx.content = ctx.content.lower()

    if ctx.author == client.user:
        return
    
    if ctx.content.startswith('--mh'):
        print('MH', ctx.content)
        await ctx.channel.send(f"Mentioning <@&747703681985544202> and <@&747703676587737229>")

    # ===== STATUS =====
    if ctx.content.startswith("--query") or ctx.content.startswith("--q"):
        response = status.query(ctx.content.lower())
        print(response)
        await ctx.channel.send(response)
        
    elif ctx.content.startswith("--add") or ctx.content.startswith("--a"):
        response = status.add(ctx.content)
        print(response)
        await ctx.channel.send(response)
        
    elif ctx.content.startswith("--update") or ctx.content.startswith("--u"):
        response = status.update(ctx.content.lower())
        print(response)
        await ctx.channel.send(response)
        
    # ===== FUNNEL =====
    # Basic Reminder
    elif ctx.content.startswith("--remind") or ctx.content.startswith("--r"):
        
        t_delta, args = funnel.remind(ctx.content)
        
        if t_delta != -1:
            await ctx.channel.send(f"Will remind you to \"{args['msg']}\" at {args['time']}")

            print('Timeout for', t_delta, 'seconds')
            await asyncio.sleep(int(t_delta))
            print('Timeout Complete')

            await ctx.channel.send(f"**Reminder:** {args['msg']}")
        else:
            await ctx.channel.send(args)
    
    # Reminder Scheduler
    elif ctx.content.startswith("--sa"):
        
        # Add to schedule and extract datetime objects
        response, timestamps, post_details = funnel.add_schedule(ctx.content)
        
        if timestamps != -1 and post_details != -1:
            await ctx.channel.send(response)
            # Schedule reminder routines
            await funnel.schedule_reminders(ctx, timestamps, post_details)
        else:
            await ctx.channel.send(response)
        
        
client.run('NzQ4NDUxMjk0OTIyMTQ1ODEz.X0dnlg.dpUItPEVNDflzXXHJhhcPEvVufU')