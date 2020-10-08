import discord
from discord.ext import commands
import asyncio
from mods import Status, Funnel

# Init Discord
intents = discord.Intents.default()
intents.members = True
bot = commands.Bot(command_prefix='--', description="Rubrix's Discord Assistant Bot", intents=intents)

# Init the Mods
status = Status()
funnel = Funnel()

print('Listening...')

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
    t_delta, params = funnel.remind(args)
        
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
    response, timestamps, post_details = funnel.add_schedule(args)

    if timestamps != -1 and post_details != -1:
        await ctx.channel.send(response)
        # Schedule reminder routines
        await funnel.schedule_reminders(ctx, timestamps, post_details)
    else:
        await ctx.channel.send(response)

# ===== Experimental Commands =====
@bot.command(aliases=['exp'])
async def test(ctx):
    
    print('Channels:', [x for x in ctx.guild.text_channels if x.name == 'discord-dev'])
    
    await ctx.channel.send('Check logs')



# =================================
# Run the bot
bot.run('NzQ4NDUxMjk0OTIyMTQ1ODEz.X0dnlg.dpUItPEVNDflzXXHJhhcPEvVufU')