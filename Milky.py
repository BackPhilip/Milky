import random 
import discord
import os
import aiohttp
import sys
import threading
import requests
from dotenv import load_dotenv
from discord.ext import commands
from discord.utils import get
from youtube_dl import YoutubeDL

load_dotenv()
bot = commands.Bot(command_prefix="~", description="Ara Ara :3")
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')
playlist = []
queueNames = []
queueCount = 0
paused = False
skipping = False
TenorToken = 'WQ0SUDCDIAJY'
milkMention = False

def update():
    threading.Timer(3.0, update).start()
    global playlist
    global queueCount
    global paused
    global skipping
    global channel
    voice = get(bot.voice_clients, guild=channel.guild)
    YDL_OPTIONS = {'format': 'bestaudio', 'noplaylist': 'True'}

    if (voice):
        if (not voice.is_playing() and len(playlist) > queueCount and not paused and not skipping):
            with YoutubeDL(YDL_OPTIONS) as ydl:
                queueCount = queueCount + 1
                info = ydl.extract_info(playlist[queueCount], download=False)
            URL = info['url']
            voice.stop()
            voice.play(discord.FFmpegPCMAudio(executable="C:/ffmpeg.exe", source=URL))
            voice.is_playing()
        if (not voice.is_playing() and len(playlist) <= queueCount and not paused and not skipping and queueCount > 0):
            playlist.clear()
            queueNames.clear()
            queueCount = 0

@bot.event
async def on_ready():
    print('Milky Online')

@bot.command()
async def hey(message):
    if message.author == bot.user:
        return

    Greeting_Quotes = [
        'Feeling lucky? Punk!',
        'You kinda smell, like a baka',
        'Having a good day?',
        'Enjoy your time here, degenerate',
        'You better have a good day🔪',
        'Say less',
        'They did surgery on a grape',
        'Go back to monki',
        'I hate avocado',
        'Nothing better to do?',
        'Normalize genocide',
        'Dogs are better than cats',
        'Tinder is like uber eats for people',
        'Bin laden is still alive',
        'Water is bad for you, drink pepsi',
        'I got scolded by jam for stomping on a puppy once',
        'Jews aren\'t that bad',
        'Fun fact, one can survive solely on milk',
        'Enjoy the next five minutes',
        'Ara ara :flushed:',
        'Baby want a bottle?',
        'Your face is very disorganized',
        'Flame said a no no word on mnf :flushed:',
        'Mix pepsi and milk, it\'s lovely, we call it pilk',
        '*moans*',
        'Choke me like you hate me but you love me',
        'Touch me with the lights on',
        'I take a mirror with me to the zoo, show it to the pandas, it freaks them out *chuckle*'
    ]

    if 1 == 1:
        response = random.choice(Greeting_Quotes)
        print('Greeted ' + str(message.author))
        await message.reply(response)


@bot.command()
async def join(ctx):
    channel = ctx.message.author.voice.channel
    voice = get(bot.voice_clients, guild=ctx.guild)
    if voice and voice.is_connected():
        await voice.move_to(channel)
        voice.play(discord.FFmpegPCMAudio(executable="C:/ffmpeg.exe", source="ara-ara.mp3"))
        print("Milky joined " + str(ctx.channel))
    else:
        voice = await channel.connect()
        voice.play(discord.FFmpegPCMAudio(executable="C:/ffmpeg.exe", source="ara-ara.mp3"))
        await ctx.reply('I pull up🕶️')
        print("Milky joined " + str(ctx.channel))

@bot.command()
async def leave(ctx):
    voice = get(bot.voice_clients, guild=ctx.guild)
    if voice and voice.is_connected:
        await voice.disconnect()
        await ctx.reply('Bbye :wave:')
        print("Milky was disconnected from " + str(ctx.message.author.voice.channel))

@bot.command()
async def play(ctx, url):
    voice = get(bot.voice_clients, guild=ctx.guild)
    global playlist
    global channel
    global queueNames
    YDL_OPTIONS = {'format': 'bestaudio', 'noplaylist': 'True'}
    channel = ctx

    if voice == None: 
        await ctx.reply("I'm not in vc :(")
        return
    if not voice == None:
        if not voice.is_playing():
            with YoutubeDL(YDL_OPTIONS) as ydl:
                info = ydl.extract_info(str(url), download=False)
                title = ydl.extract_info(str(url), download=False).get("title", None)
                embedVar = discord.Embed(title="Song started :play_pause:", description=title, color=0xf900ff)
            URL = info['url']
            queueNames.append(title)
            playlist.append(URL)
            voice.play(discord.FFmpegPCMAudio(executable="C:/ffmpeg.exe", source=playlist[queueCount]))
            voice.is_playing()
            await ctx.reply(embed=embedVar)
            update()
        else:
            with YoutubeDL(YDL_OPTIONS) as ydl:
                info = ydl.extract_info(url, download=False)
                title = ydl.extract_info(url, download=False).get("title", None)
                embedVar = discord.Embed(title="Song queued :bookmark:", description=title, color=0xf900ff)
            URL = info['url']
            queueNames.append(title)
            playlist.append(URL)
            await ctx.reply(embed=embedVar)

@bot.command()
async def remove(ctx, number):
    global playlist
    global queueNames
    global queueCount
    position = int(number) - 1

    if position <= queueCount:
        await ctx.reply(str(queueNames[position]) + "\nAlready played, can't do that")
    else:
        embedVar = discord.Embed(title="Removed :negative_squared_cross_mark:", description=str(queueNames[position]), color=0xf900ff)
        await ctx.reply(embed=embedVar)
        del playlist[position]
        del queueNames[position]
    
@bot.command()
async def np(ctx):
    global queueNames
    global queueCount
    voice = get(bot.voice_clients, guild=ctx.guild)

    if not voice.is_playing():
        embedVar = discord.Embed(title="Nothing playing", description=":octagonal_sign:", color=0xf900ff)
        await ctx.reply(embed=embedVar)
    else:
        embedVar = discord.Embed(title="Now playing :play_pause:", description=str(queueNames[queueCount]), color=0xf900ff)
        await ctx.reply(embed=embedVar)

@bot.command()
async def queue(ctx):
    global queueNames
    count = 1
    embedVar = discord.Embed(title="Music queue", description=":bookmark:", color=0xf900ff)
    for t in queueNames:
        embedVar.add_field(name=str(count) + ". " + t, value="------------------------", inline=False)
        count += 1

    if (len(queueNames) == 0):
        await ctx.reply("No songs in queue :(")
    else: 
        await ctx.reply(embed=embedVar)

@bot.command()
async def skip(ctx):
    global queueCount
    global playlist
    global queueNames
    global skipping
    voice = get(bot.voice_clients, guild=ctx.guild)

    if len(playlist) > queueCount:
        skipping = True
        YDL_OPTIONS = {'format': 'bestaudio', 'noplaylist': 'True'}
        voice = get(bot.voice_clients, guild=ctx.guild)
        voice.stop()
        embedVar = discord.Embed(title="Skipped :track_next:", description=str(queueNames[queueCount]), color=0xf900ff)
        await ctx.reply(embed=embedVar)
        queueCount = queueCount + 1
        with YoutubeDL(YDL_OPTIONS) as ydl:
            info = ydl.extract_info(playlist[queueCount], download=False)
        URL = info['url']
        voice.play(discord.FFmpegPCMAudio(executable="C:/ffmpeg.exe", source=URL))
        voice.is_playing()
        embedVar = discord.Embed(title="Started playing :play_pause:", description=str(queueNames[queueCount]), color=0xf900ff)
        await ctx.reply(embed=embedVar)
        skipping = False
    else: await ctx.reply("Nothing to skip :(")


@bot.command()
async def resume(ctx):
    voice = get(bot.voice_clients, guild=ctx.guild)
    global paused

    if not voice.is_playing():
        voice.resume()
        paused = False
        await ctx.reply('Resuming :play_pause:')
    else: await ctx.reply('Already playing :play_pause:')


@bot.command()
async def pause(ctx):
    voice = get(bot.voice_clients, guild=ctx.guild)
    global paused

    if voice.is_playing():
        voice.pause()
        paused = True
        await ctx.reply('Hold up :pause_button:')
    else: await ctx.reply('Nothing to pause :pause_button:')


@bot.command()
async def stop(ctx):
    voice = get(bot.voice_clients, guild=ctx.guild)
    global playlist
    global queueNames
    global queueCount

    voice.stop()
    playlist.clear()
    await ctx.reply(str(len(queueNames)) + ' songs removed :wave:')
    queueNames.clear()
    queueCount = 0


@bot.command()
async def clear(ctx, amount=100000):
    await ctx.channel.purge(limit=amount)
    await ctx.send("Fine keep your secrets, messages have been deleted 🤨")

    if amount == 100000: print ("All messages cleared from " + str(ctx.channel))
    else: print (str(amount) + " messages cleared from " + str(ctx.channel))

@bot.command(pass_context=True)
async def meme(ctx):
  embed = discord.Embed(title="Some memes :smirk:", description="")
  async with aiohttp.ClientSession() as cs:
    async with cs.get(
        'https://www.reddit.com/r/memes/new.json?sort=hot') as r:
        res = await r.json()
        embed.set_image(url=res['data']['children'][random.randint(0, 25)]['data']['url'])
        await ctx.reply(embed=embed)
        print (str(ctx.author) + " asked for a meme")
    
@bot.command(pass_context=True)
async def dance(ctx):
    response = requests.get("https://g.tenor.com/v1/search?q={}&key={}&limit=20".format('anime dance', TenorToken))
    data = response.json()
    output = random.choice(data["results"])
    gif = output['media'][0]['gif']['url']
    embed = discord.Embed(title="Rythm of the night", description="")
    embed.set_image(url=gif)
    print (str(ctx.author) + " danced")
    await ctx.reply(embed=embed)

@bot.command(pass_context=True)
async def kiss(ctx, member : discord.Member):
    response = requests.get("https://g.tenor.com/v1/search?q={}&key={}&limit=20".format('anime kiss', TenorToken))
    data = response.json()
    output = random.choice(data["results"])
    gif = output['media'][0]['gif']['url']
    embed = discord.Embed(title=" <3 ", description=ctx.author.mention + " kisses " + member.mention)
    embed.set_image(url=gif)
    print (str(ctx.author) + " kissed " + str(member))
    await ctx.reply(embed=embed) 

@bot.command(pass_context=True)
async def slap(ctx, member : discord.Member):
    response = requests.get("https://g.tenor.com/v1/search?q={}&key={}&limit=20".format('anime slap', TenorToken))
    data = response.json()
    output = random.choice(data["results"])
    gif = output['media'][0]['gif']['url']
    embed = discord.Embed(title=":rotating_light:", description=ctx.author.mention + " slaps " + member.mention)
    embed.set_image(url=gif)
    await ctx.reply(embed=embed) 
    print (str(ctx.author) + " slapped " + str(member))

@bot.command(pass_context=True)
async def pat(ctx, member : discord.Member):
    response = requests.get("https://g.tenor.com/v1/search?q={}&key={}&limit=20".format('anime pat', TenorToken))
    data = response.json()
    output = random.choice(data["results"])
    gif = output['media'][0]['gif']['url']
    embed = discord.Embed(title=":blush:", description=ctx.author.mention + " pats " + member.mention)
    embed.set_image(url=gif)
    await ctx.reply(embed=embed) 
    print (str(ctx.author) + " patted " + str(member))

@bot.command(pass_context=True)
async def hug(ctx, member : discord.Member):
    response = requests.get("https://g.tenor.com/v1/search?q={}&key={}&limit=20".format('anime hug', TenorToken))
    data = response.json()
    output = random.choice(data["results"])
    gif = output['media'][0]['gif']['url']
    embed = discord.Embed(title=":blush:", description=ctx.author.mention + " hugs " + member.mention)
    embed.set_image(url=gif)
    await ctx.reply(embed=embed)
    print (str(ctx.author) + " hugged " + str(member))

@bot.command(pass_context=True)
async def levi(ctx):
    response = requests.get("https://g.tenor.com/v1/search?q={}&key={}&limit=20".format('levi ackerman', TenorToken))
    data = response.json()
    output = random.choice(data["results"])
    gif = output['media'][0]['gif']['url']
    embed = discord.Embed(title="Levi Ackerman", description="Give up on your dreams and die")
    embed.set_image(url=gif)
    await ctx.reply(embed=embed)
    print ("Levi was summoned")

@bot.command(pass_context=True)
async def fuck(ctx, member : discord.Member):
    response = requests.get("https://g.tenor.com/v1/search?q={}&key={}&limit=20".format('anime sex', TenorToken))
    data = response.json()
    output = random.choice(data["results"])
    gif = output['media'][0]['gif']['url']
    embed = discord.Embed(title=":flushed:", description=ctx.author.mention + " fucks " + member.mention)
    embed.set_image(url=gif)
    await ctx.reply(embed=embed)
    print(str(ctx.author) + " fucked " + str(member))

@bot.command(pass_context=True)
async def attack(ctx):
    response = requests.get("https://g.tenor.com/v1/search?q={}&key={}&limit=20".format('anime girl gun', TenorToken))
    data = response.json()
    output = random.choice(data["results"])
    gif = output['media'][0]['gif']['url']
    embed = discord.Embed(title="Yessir", description="It go ratatatata")
    embed.set_image(url=gif)
    await ctx.reply(embed=embed)
    print("I attacked")

@bot.event
async def on_message(ctx):
    global milkMention
    if ctx.author == bot.user:
        return

    if milkMention:
        if 'fuck you' in ctx.content.lower():
            await ctx.reply('Fuck me then:flushed:')
            milkMention = False
        elif 'shut up' in ctx.content.lower() or 'stfu' in ctx.content.lower():
            await ctx.reply('How about you shut up, twat')
            milkMention = False
        elif 'love' in ctx.content.lower():
            await ctx.reply('What is love?')
            milkMention = False
        elif 'bot' in ctx.content.lower():
            await ctx.reply('I\'m a real girl, not a bot :pensive:')
            milkMention = False
        elif 'istg' in ctx.content.lower():
            await ctx.reply('I thought you were an atheist')
            milkMention = False
        elif 'suck' in ctx.content.lower():
            await ctx.reply('I do suck :smirk:')
            milkMention = False
    
    if ('happy' in ctx.content.lower()):
        print("Read happy from " + str(ctx.author))
        await ctx.reply('Imagine being asked :rolling_eyes:')


    if 'milky' in ctx.content.lower():
        if 'fuck you' in ctx.content.lower():
            milkMention = False
            await ctx.reply('Fuck me then:flushed:')
        elif 'shut up' in ctx.content.lower():
            milkMention = False
            await ctx.reply('How about you shut up, twat')
        elif 'love' in ctx.content.lower():
            milkMention = False
            await ctx.reply('What is love?')
        elif 'bot' in ctx.content.lower():
            milkMention = False
            await ctx.reply('I\'m a real girl, not a bot :pensive:')
        elif 'istg' in ctx.content.lower():
            milkMention = False
            await ctx.reply('I thought you were an atheist')
        elif 'suck' in ctx.content.lower():
            milkMention = False
            await ctx.reply('I do suck :smirk:')
        else:
            await ctx.reply(':flushed:')
            milkMention = True
        print(str(ctx.author) + " mentioned my name")

    if 'dickhead' in ctx.content.lower() or 'nigg' in ctx.content.lower():
        await ctx.reply('Bad word baka 🤨')
        await ctx.delete()
        print(str(ctx.author) + " swore")

    if 'choke' in ctx.content.lower():
        print("Read choke from " + str(ctx.author))
        await ctx.reply('Choke me like you hate me, but you love me :blush:')

    await bot.process_commands(ctx)

@kiss.error
async def kiss_error(ctx, error):
    if str(error) == "member is a required argument that is missing.":
        await ctx.reply('Tag someone to kiss :rolling_eyes:')
    else:
        print(str(error))

@hug.error
async def hug_error(ctx, error):
    if str(error) == "member is a required argument that is missing.":
        await ctx.reply('Tag someone to hug :rolling_eyes:')
    else:
        print(str(error))

@fuck.error
async def fuck_error(ctx, error):
    if str(error) == "member is a required argument that is missing.":
        await ctx.reply('Tag someone to fuck :rolling_eyes:')
    else:
        print(str(error))

@slap.error
async def slap_error(ctx, error):
    if str(error) == "member is a required argument that is missing.":
        await ctx.reply('Tag someone to slap :rolling_eyes:')
    else:
        print(str(error))

@pat.error
async def pat_error(ctx, error):
    if str(error) == "member is a required argument that is missing.":
        await ctx.reply('Tag someone to pat :rolling_eyes:')
    else:
        print(str(error))

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, discord.ext.commands.errors.CommandNotFound):
        await ctx.reply("I don't know that command")
    if str(error) == "member is a required argument that is missing.":
        None
@levi.error
async def levi_error(ctx, error):
    print(str(error))

bot.run(TOKEN)