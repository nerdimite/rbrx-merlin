import discord
from discord.ext import commands
import asyncio
from mods import Status, Scheduler, NewsBot
import os
from utils import update_reminders

# Init Discord
intents = discord.Intents.default()
intents.members = True
bot = commands.Bot(command_prefix='--', description="Rubrix's Discord Assistant Bot", intents=intents)

# Init the Mods
status = Status()
scheduler = Scheduler()
newsbot = NewsBot()

# ===== Run Background Tasks =====
@bot.event
async def on_ready():
    print('Listening...')
    # Scheduler
    scheduler_task = asyncio.create_task(scheduler.run_scheduler(bot))
    # Newsbot
    newsbot_task = asyncio.create_task(newsbot.run(bot))
    
    await scheduler_task
    await newsbot_task

@bot.event
async def on_member_remove(member):
    status.member_remove(member)
    

# ===== Status Sheet Commands =====
@bot.command(aliases=['q'])
async def query(ctx, *, args):
    response = status.query(args)
    print(response)
    await ctx.channel.send(response)
    
@bot.command(aliases=['a'])
async def add(ctx, *, args):
    response = status.add(args)
    print(response)
    await ctx.channel.send(response)

@bot.command(aliases=['u'])
async def update(ctx, *, args):
    response = status.update(args)
    print(response)
    await ctx.channel.send(response)

# ===== Scheduling Commands =====
@bot.command(aliases=['r'])
async def remind(ctx, *, args):
    t_delta, params = scheduler.remind(args)
        
    if t_delta != -1:
        await ctx.channel.send(f"Will remind you to \"{params['msg']}\" at {params['time']}")

        print('Timeout for', t_delta, 'seconds')
        await asyncio.sleep(int(t_delta))
        print('Timeout Complete')

        await ctx.channel.send(f"**Reminder:** {params['msg']}")
    else:
        await ctx.channel.send(params)

@bot.command(aliases=['s'])
async def schedule(ctx, *, args):
    # Add to schedule and extract datetime objects
    response, timestamps, post_details = scheduler.get_schedule(args)

    if timestamps != -1 and post_details != -1:
        # Get reminders
        reminders = scheduler.get_reminders(timestamps, post_details)
        # Save reminders
        update_reminders(reminders)
        
    await ctx.channel.send(response)


# ===== Experimental Commands =====
@bot.command(aliases=['ping'])
async def test(ctx, *, args):
    
    print('Members', ctx.guild.members)
    
    print('You said', args)
    
    await ctx.channel.send('You said {}'.format(args))
    


# =================================
# Run the bot
token = os.environ['DISCORD']
bot.run(token)