import random 
import discord
import os
import aiohttp
import sys
import threading
import requests
import enchant
from dotenv import load_dotenv
from discord.ext import commands
from discord.utils import get
from youtube_dl import YoutubeDL

intents = discord.Intents.default()
intents.members = True

load_dotenv()
bot = commands.Bot(command_prefix="~", intents=intents)
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')
TenorToken = os.getenv('TENOR')

playlist = []
queueNames = []
queueCount = 0
paused = False
skipping = False

milkMention = False
silenced = False

deletedMessages = []
deletedMessageUsers = []
deletedCount = 0
editedMessage = ''

gameInProgress = False
scoreNames = []
scores = []
questions = ['AFT', 'TAC', 'ITT', 'AFT', 'THA', 'APT', 'DESE', 'UTI', 'ESE', 'TUI', 'IRM', 'GRA', 'TTA', 'SAM', 'TRE', 'AL', 'DI', 
            'FU', 'CK', 'PLA', 'TER', 'LEG', 'PA', 'RA', 'ME', 'AT', 'EDE', 'MEL', 'EL', 'QUE', 'AN', 'BLE', 'OY', 'TW', 'OUB', 'NEL', 'NO', 'TOR', 
            'LA', 'PH']
botrps = ['🪨', '🧻', '✂️']
dictionary = enchant.Dict("en_US")
currentQuestion = ''
gameChannel = ''

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

@bot.event
async def on_member_join(member):
    channel = bot.get_channel(893943538201526284)
    response = requests.get("https://g.tenor.com/v1/search?q={}&key={}&limit=20".format('anime welcome', TenorToken))
    data = response.json()
    output = random.choice(data["results"])
    gif = output['media'][0]['gif']['url']
    embed=discord.Embed(title="Welcome Degenerate",description=f"{member.mention} Just Joined")
    embed.set_image(url=gif)
    role = discord.utils.get(member.guild.roles, name='Common Folk')
    await member.add_roles(role)
    print (str(member) + " joined the server")
    await channel.send(embed=embed)

@bot.event
async def on_member_remove(member):
    channel = bot.get_channel(893943538201526284)
    response = requests.get("https://g.tenor.com/v1/search?q={}&key={}&limit=20".format('anime cry', TenorToken))
    data = response.json()
    output = random.choice(data["results"])
    gif = output['media'][0]['gif']['url']
    embed=discord.Embed(title="Member Left",description=f"{member.mention} Just Left the server")
    embed.set_image(url=gif)
    print (str(member) + " left the server")
    await channel.send(embed=embed)

@bot.event
async def on_message_delete(message):
    global deletedMessages
    global deletedMessageUsers
    global deletedCount

    if deletedCount > 5:
        deletedCount = 0

    deletedMessages.insert(deletedCount, message)
    deletedMessageUsers.insert(deletedCount, str(message.author))
    deletedCount =+ 1
    print ("Deleted: " + str(message.content) + " by " + str(message.author))

@bot.event
async def on_message_edit(message_before, message_after):
    global editedMessage
    editedMessage = discord.Embed(title=str(message_before.author) + " edited a message")
    editedMessage.add_field(name="Before", value=message_before.content, inline=True)
    editedMessage.add_field(name="After", value=message_after.content, inline=True)

@bot.command()
async def stats(ctx):
    with open('messageCount.txt', 'r+', encoding='utf-8') as file:
            messageCount = file.readlines() 
            embed=discord.Embed(title=f"Server statistics for {ctx.guild.name}", color=0xff00f6)
            embed.add_field(name="Users:", value=ctx.guild.member_count, inline=False)
            embed.add_field(name="Channels:", value=len(ctx.guild.channels), inline=False)
            embed.add_field(name="Messages Sent:", value=messageCount[0] + " from 1/1/2022", inline=False)
            await ctx.reply(embed=embed)

@bot.command()
async def balance(ctx, member : discord.Member):
    names = []
    counts = []   
    myCount = ''   
    with open('milkNames.txt', 'r') as file:
        names = file.readlines()
    with open('milkCounts.txt', 'r') as file:
        counts = file.readlines()                                                         
    lineIndex = -1
    for name in names:
        if str(name).strip() == str(member):
            lineIndex = names.index(name)
    if not lineIndex == -1:
        for i, line in enumerate(counts):
            if i == lineIndex:                                            
                myCount = line.strip()
                embed = discord.Embed(title=myCount + " milk :milk:", color=0xff00f6)
                await ctx.reply(embed=embed)
    else:
        embed = discord.Embed(title="You have no milk")
        await ctx.reply(embed=embed)

@bot.command()
async def transfer(ctx, count, member : discord.Member):
    if(takeMilk(str(ctx.author), int(count))):
        giveMilk(str(member), int(count))
        embed = discord.Embed(title=count + " milk given to " + str(member), color=0xff00f6)
        await ctx.reply(embed=embed)
        print(str(ctx.author) + " gave " + count + " milk to " + str(member))
    else:
        embed = discord.Embed(title="You don't have enough milk", color=0xff00f6)
        await ctx.reply(embed=embed)

@bot.command()
async def edited(ctx):
    global editedMessage
    await ctx.reply(embed=editedMessage)

@bot.command()
async def vote(ctx):
    title = ctx.message.content.removeprefix('~vote ')
    print(str(ctx.author) + " inititiated a vote: " + title)
    embed=discord.Embed(title=title, description= "by " + ctx.author.mention, color=0xff00f6)
    sent = await ctx.send(embed=embed)
    await sent.add_reaction('✅')
    await sent.add_reaction('❌')

@bot.command()
async def game(ctx, param):
    global gameInProgress
    global scoreNames
    global scores
    global questions
    global currentQuestion
    global gameChannel

    if gameInProgress:
        embed=discord.Embed(title="Game already in progress", description= "First finish the game in progress to start another")

    elif param == 'start':
        scores.clear()
        gameChannel = ctx.channel

        response = requests.get("https://g.tenor.com/v1/search?q={}&key={}&limit=20".format('anime start', TenorToken))
        data = response.json()
        output = random.choice(data["results"])
        gif = output['media'][0]['gif']['url']
        embed=discord.Embed(title="Game started", description= "by " + ctx.author.mention)
        embed.set_image(url=gif)

        question = random.choice(questions)
        currentQuestion = question
        gameInProgress = True
        questionEmbed=discord.Embed(title=question, description= "get a word")

        await ctx.send(embed=embed)
        await ctx.send(embed=questionEmbed)
        print(str(ctx.author) + " started a game: ")

    if param == 'score':
        embed=discord.Embed(title="Scores", description="----------------------------------------------------------", color=0xff00f6)
        for ind, entry in enumerate(scoreNames):
            embed.add_field(name=entry, value=str(scores[ind]), inline=True)
        await ctx.send(embed=embed)

@bot.command()
async def rps(ctx, move, wager):
    global botrps
    botChoice = random.choice(botrps)
    embed=discord.Embed(title="none", description="none", color=0xff00f6)
    won = False
    lost = False

    if int(milkCount(str(ctx.author))) >= int(wager):
        if move == 'rock' or move == 'r':
            if botChoice == '🪨':
                embed=discord.Embed(title="🪨 vs 🪨", description="Tie", color=0xff00f6)
            elif botChoice == '🧻':
                embed=discord.Embed(title="🪨 vs 🧻", description="You lose " + wager + " milk", color=0xff00f6)
                lost = True
            elif botChoice == '✂️':
                embed=discord.Embed(title="🪨 vs ✂️", description="You win " + wager + " milk", color=0xff00f6)
                won = True
        elif move == 'paper' or move == 'p':
            if botChoice == '🪨':
                embed=discord.Embed(title="🧻 vs 🪨", description="You win " + wager + " milk", color=0xff00f6)
                won = True
            elif botChoice == '🧻':
                embed=discord.Embed(title="🧻 vs 🧻", description="Tie", color=0xff00f6)
            elif botChoice == '✂️':
                embed=discord.Embed(title="🧻 vs ✂️", description="You lose " + wager + " milk", color=0xff00f6)
                lost = True
        elif move == 'scissors' or move == 's':
                if botChoice == '🪨':
                    embed=discord.Embed(title="✂️ vs 🪨", description="You lose " + wager + " milk", color=0xff00f6)
                    lost = True
                elif botChoice == '🧻':
                    embed=discord.Embed(title="✂️ vs 🧻", description="You win " + wager + " milk", color=0xff00f6)
                    won = True
                elif botChoice == '✂️':
                    embed=discord.Embed(title="✂️ vs ✂️", description="Tie", color=0xff00f6)
        else:
                embed=discord.Embed(title="Incorrect input", description="rock, paper, scissors", color=0xff00f6)
            
        await ctx.reply(embed=embed)
        if won:
            giveMilk(str(ctx.author), int(wager))
            print(str(ctx.author) + " won " + wager + " milk")
        elif lost:
            takeMilk(str(ctx.author), int(wager))
            print(str(ctx.author) + " lost " + wager + " milk")
    else:
        embed = discord.Embed(title="You don't have enough milk", color=0xff00f6)
        await ctx.reply(embed=embed)


@bot.command()
async def silence(ctx):
    global silenced
    if ctx.message.author.guild_permissions.administrator:
        if not silenced:
            embed=discord.Embed(title="Silenced chat", description="The chat has been silenced, only admins can talk")
            silenced = True
            print(str(ctx.author) + " silenced chat")
            await ctx.send(embed=embed)
        else:
            embed=discord.Embed(title="Chat active", description="The chat has been activated, everyone can talk")
            silenced = False
            print(str(ctx.author) + " activated chat")
            await ctx.send(embed=embed)
    else:
        embed=discord.Embed(title="Permission Denied.", description="You don't have permission to use this command.", color=0xff00f6)
        await ctx.reply(embed=embed)

@bot.command()
async def expose(ctx, member : discord.Member):
    global deletedMessages
    global deletedMessageUsers
    count = 0
    found = False

    for ind, user in enumerate(deletedMessageUsers):
        if (user == str(member)):
            if count < 5:
                if not found:
                    embed=discord.Embed(title="Exposed", description=member.mention)
                    found = True
                embed.add_field(name=str(deletedMessages[ind].content), value="-----------------------------", inline=False)
                count += 1
    
    if (not found):
        await ctx.reply("Nothing to expose")
    else:
        await ctx.reply(embed=embed)
        print(str(ctx.author) + " exposed " + str(member))

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
    else:
        await ctx.reply('Not connected')

@bot.command()
async def say(ctx):
    channel = ctx.message.author.voice.channel
    voice = get(bot.voice_clients, guild=ctx.guild)
    say = ctx.message.content.removeprefix('~say')

    if not voice.is_playing():
        if voice and voice.is_connected():
            await voice.move_to(channel)
            await ctx.send(str(say), tts=True)
            voice.stop()
        else:
            voice = await channel.connect()
            await ctx.send(str(say), tts=True)
            voice.stop()
            print("Milky joined " + str(ctx.channel))
    else: await ctx.reply("Can't right now :(")

@bot.command()
async def play(ctx, url):
    voice = get(bot.voice_clients, guild=ctx.guild)
    global playlist
    global channel
    global queueNames
    vc = ctx.message.author.voice.channel
    YDL_OPTIONS = {'format': 'bestaudio', 'noplaylist': 'True'}
    channel = ctx
    if voice == None: 
        voice = await vc.connect()
        await ctx.reply('I pull up🕶️')
        print("Milky joined " + str(ctx.channel))
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
async def vibe(ctx):
    global playlist
    global queueNames
    global queueCount
    global channel
    vc = ctx.message.author.voice.channel
    YDL_OPTIONS = {'format': 'bestaudio', 'noplaylist': 'True'}
    voice = get(bot.voice_clients, guild=ctx.guild)
    file = ctx.message.content.removeprefix('~vibe ') + ".txt"
    custom = open(file, "r")

    channel = ctx

    for line in custom:
        if (line != ""):
            if voice == None: 
                voice = await vc.connect()
                await ctx.reply('I pull up🕶️')
                print("Milky joined " + str(ctx.channel))
            if not voice.is_playing():
                with YoutubeDL(YDL_OPTIONS) as ydl:
                    info = ydl.extract_info(str(line), download=False)
                    title = ydl.extract_info(str(line), download=False).get("title", None)
                    embedVar = discord.Embed(title="Song started :play_pause:", description=title, color=0xf900ff)
                URL = info['url']
                queueNames.append(title)
                playlist.append(URL)
                voice.play(discord.FFmpegPCMAudio(executable="C:/ffmpeg.exe", source=playlist[queueCount]))
                voice.is_playing()
                update()
                await ctx.reply(embed=embedVar)
            else:
                with YoutubeDL(YDL_OPTIONS) as ydl:
                    info = ydl.extract_info(line, download=False)
                    title = ydl.extract_info(line, download=False).get("title", None)
                URL = info['url']
                queueNames.append(title)
                playlist.append(URL)

@bot.command()
async def remove(ctx, number):
    global playlist
    global queueNames
    global queueCount
    position = int(number) - 1

    if len(queueNames) == 0:
        await ctx.reply("No songs in queue :(")
    elif position > len(queueNames) - 1:
        await ctx.reply("No song in that position :(")
    else:
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
    if ctx.message.author.guild_permissions.administrator:
        await ctx.channel.purge(limit=amount)
        await ctx.send("Fine keep your secrets, messages have been deleted 🤨")
        if amount == 100000: print ("All messages cleared from " + str(ctx.channel))
        else: print (str(amount) + " messages cleared from " + str(ctx.channel))
    else:
        embed=discord.Embed(title="Permission Denied.", description="You don't have permission to use this command.", color=0xff00f6)
        await ctx.reply(embed=embed)

@bot.command(pass_context=True)
async def meme(ctx):
  embed = discord.Embed(title="Some memes :smirk:, 10 milk deducted", description="")
  async with aiohttp.ClientSession() as cs:
    async with cs.get(
        'https://www.reddit.com/r/memes/new.json?sort=hot') as r:
        res = await r.json()
        embed.set_image(url=res['data']['children'][random.randint(0, 25)]['data']['url'])
        await ctx.reply(embed=embed)
        takeMilk(str(ctx.author), 10)
        print (str(ctx.author) + " asked for a meme")

@bot.command(pass_context=True)
async def hentai(ctx):
    if (ctx.channel.is_nsfw()):
        if int(milkCount(str(ctx.author))) >= 100:
            embed = discord.Embed(title="Some hentai:smirk:, 100 milk deducted", description="")
            async with aiohttp.ClientSession() as cs:
                async with cs.get(
                    'https://www.reddit.com/r/hentai/new.json?sort=top&t=year') as r:
                    res = await r.json()
                    embed.set_image(url=res['data']['children'][random.randint(0, 25)]['data']['url'])
                    await send_dm(ctx=ctx, member=ctx.author, content=embed)
                    takeMilk(str(ctx.author), 100)
                    print (str(ctx.author) + " asked for hentai")
        else:
            embed = discord.Embed(title="Not enough milk", description="")
            await ctx.reply(embed=embed)
    else:
        embed = discord.Embed(title="Not NSFW :rotating_light:", description="Mf go to NSFW")
        await ctx.reply(embed=embed)

@bot.command(pass_context=True)
async def yaoi(ctx):
    if (ctx.channel.is_nsfw()):
        if int(milkCount(str(ctx.author))) >= 100:
            embed = discord.Embed(title="Some yaoi :smirk, 100 milk deducted:", description="")
            async with aiohttp.ClientSession() as cs:
                async with cs.get(
                    'https://www.reddit.com/r/yaoi/new.json?sort=top&t=year') as r:
                    res = await r.json()
                    embed.set_image(url=res['data']['children'][random.randint(0, 25)]['data']['url'])
                    await send_dm(ctx=ctx, member=ctx.author, content=embed)
                    takeMilk(str(ctx.author), 100)
                    print (str(ctx.author) + " asked for yaoi")
        else:
            embed = discord.Embed(title="Not enough milk", description="")
            await ctx.reply(embed=embed)
    else:
        embed = discord.Embed(title="Not NSFW :rotating_light:", description="Mf go to NSFW")
        await ctx.reply(embed=embed)

@bot.command(pass_context=True)
async def tenor(ctx, search):
    response = requests.get("https://g.tenor.com/v1/search?q={}&key={}&limit=20".format(str(search), TenorToken))
    data = response.json()
    output = random.choice(data["results"])
    gif = output['media'][0]['gif']['url']
    embed = discord.Embed(title="Tenor", description="")
    embed.set_image(url=gif)
    print (str(ctx.author) + " searched for " + str(search))
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
async def tie(ctx, member : discord.Member):
    response = requests.get("https://g.tenor.com/v1/search?q={}&key={}&limit=20".format('tie up', TenorToken))
    data = response.json()
    output = random.choice(data["results"])
    gif = output['media'][0]['gif']['url']
    embed = discord.Embed(title=":flushed:", description=ctx.author.mention + " ties down " + member.mention)
    embed.set_image(url=gif)
    await ctx.reply(embed=embed)
    print(str(ctx.author) + " tied down " + str(member))

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

@bot.command()
async def tcommands(ctx):
    embedVar = discord.Embed(title="Text Commands", description="Command Prefix: ~", color=0xf900ff)

    embedVar.add_field(name="hey", value="return a random reply", inline=False)
    embedVar.add_field(name="stats", value="displays server statistics", inline=False)
    embedVar.add_field(name="meme", value="returns a fresh meme", inline=False)
    embedVar.add_field(name="dance", value="returns a dancing gif", inline=False)
    embedVar.add_field(name="kiss", value="@ someone to kiss them", inline=False)
    embedVar.add_field(name="pat", value="@ someone to pat them", inline=False)
    embedVar.add_field(name="slap", value="@ someone to slap them", inline=False)
    embedVar.add_field(name="hug", value="@ someone to hug them", inline=False)
    embedVar.add_field(name="fuck", value="@ someone to fuck them", inline=False)
    embedVar.add_field(name="tie", value="@ someone to tie them up", inline=False)
    embedVar.add_field(name="attack", value="returns an attacking gif", inline=False)

    await ctx.reply(embed=embedVar)
    print (str(ctx.message.author) + " asked for help")

@bot.command()
async def vcommands(ctx):
    embedVar = discord.Embed(title="Voice Commands", description="Command Prefix: ~", color=0xf900ff)

    embedVar.add_field(name="join", value="I join the vc", inline=False)
    embedVar.add_field(name="play", value="follow it with a youtube link to play that song", inline=False)
    embedVar.add_field(name="vibe", value="follow it with (basic, rap, sad or corpse) for a playlist", inline=False)
    embedVar.add_field(name="queue", value="Show songs in queue", inline=False)
    embedVar.add_field(name="say", value="follow it with something to say text-to-speech", inline=False)
    embedVar.add_field(name="leave", value="I leave the vc", inline=False)

    await ctx.reply(embed=embedVar)
    print (str(ctx.message.author) + " asked for help")

@bot.event
async def on_message(ctx):
    global milkMention
    global silenced
    global gameInProgress
    global scoreNames
    global scores
    global questions
    global dictionary
    global currentQuestion
    global gameChannel

    if ctx.author == bot.user:
        return

    if ctx.guild.id == 893943537698213949:
        with open('messageCount.txt', 'r+', encoding='utf-8') as file:
            messageCount = file.readlines() 
            messageCount[0] = str(int(messageCount[0]) + 1)
            with open('messageCount.txt', 'w') as file:
                        file.writelines(messageCount) 

    if gameInProgress:
        if ctx.channel == gameChannel:
            if not ('~game start' in ctx.content.lower()):
                if not ('~game stop' in ctx.content.lower()):
                    if dictionary.check(ctx.content.lower()):
                        if currentQuestion.lower() in ctx.content.lower():
                            await ctx.add_reaction('✅')
                            question = random.choice(questions)
                            currentQuestion = question
                            gameInProgress = True
                            user = ''
                            index = -1
                            for ind, name in enumerate(scoreNames):
                                if str(ctx.author) == name:
                                    index = ind
                            if index == -1:
                                scoreNames.append(str(ctx.author))
                                scores.append(1)
                            else:
                                scores[index] = scores[index] + 1
                            if scores[index] == 10:
                                giveMilk(str(ctx.author), 100)

                                scoreembed=discord.Embed(title="Scores", description="----------------------------------------------------------", color=0xff00f6)
                                for ind, entry in enumerate(scoreNames):
                                    scoreembed.add_field(name=entry, value=str(scores[ind]), inline=True)
                                await ctx.reply(embed=scoreembed)
                                wonembed=discord.Embed(title=str(ctx.author) + " Won", description="Congratulations, here is 100 milk 🥛", color=0xff00f6)
                                await ctx.reply(embed=wonembed)

                                scores.clear()
                                scoreNames.clear()
                                gameInProgress = False
                                currentQuestion = ''
                                print(str(ctx.author) + ' won 100 milk')
                            else:
                                questionEmbed=discord.Embed(title=question, description= "Score: " + str(scores[index]), color=0xff00f6)
                                await ctx.reply(embed=questionEmbed)
                        else: await ctx.add_reaction('❌')
                    else: await ctx.add_reaction('❌')
                else: 
                    scoreembed=discord.Embed(title="Scores", description="----------------------------------------------------------", color=0xff00f6)
                    for ind, entry in enumerate(scoreNames):
                        scoreembed.add_field(name=entry, value=str(scores[ind]), inline=True)
                    await ctx.reply(embed=scoreembed)     

                    scores.clear()
                    scoreNames.clear()
                    gameInProgress = False
                    currentQuestion = ''   
                
                    response = requests.get("https://g.tenor.com/v1/search?q={}&key={}&limit=20".format('anime stop', TenorToken))
                    data = response.json()
                    output = random.choice(data["results"])
                    gif = output['media'][0]['gif']['url']
                    embed=discord.Embed(title="Game stopped", description= "by " + ctx.author.mention, color=0xff00f6)
                    embed.set_image(url=gif)
                    await ctx.reply(embed=embed)
            else: await ctx.reply("Can't, game in progress")

    if silenced:
        if not ctx.author.guild_permissions.administrator:
            await ctx.delete()

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

    if 'nigg' in ctx.content.lower():
        await ctx.reply('Bad word baka 🤨')
        await ctx.delete()
        print(str(ctx.author) + " swore")

    if 'choke' in ctx.content:
        print("Read choke from " + str(ctx.author))
        await ctx.reply('Choke me like you hate me, but you love me :blush:')

    if '💀' in ctx.content.lower():
        await ctx.channel.send('💀')

    await bot.process_commands(ctx)

@bot.command(pass_context = True)
async def mute(ctx, member: discord.Member):
     if ctx.message.author.guild_permissions.administrator:
        role = discord.utils.get(member.guild.roles, name='Muted')

        await member.edit(roles=[])
        await member.add_roles(role)
        embed=discord.Embed(title="Muted!", description="**{0}** was muted by **{1}**!".format(member, ctx.message.author), color=0xff00f6)
        print(str(ctx.message.author) + " Muted " + str(member))
        await ctx.reply(embed=embed)
     else:
        embed=discord.Embed(title="Permission Denied.", description="You don't have permission to use this command.", color=0xff00f6)
        await ctx.reply(embed=embed)

@bot.command(pass_context = True)
async def unmute(ctx, member: discord.Member):
     if ctx.message.author.guild_permissions.administrator:
        role = discord.utils.get(member.guild.roles, name='Common Folk')
        await member.edit(roles=[])
        await member.add_roles(role)
        embed=discord.Embed(title="Unmuted!", description="**{0}** was unmuted by **{1}**!".format(member, ctx.message.author), color=0xff00f6)
        print(str(ctx.message.author) + " Unmuted " + str(member))
        await ctx.reply(embed=embed)
     else:
        embed=discord.Embed(title="Permission Denied.", description="You don't have permission to use this command.", color=0xff00f6)
        await ctx.reply(embed=embed)

@bot.command(pass_context = True)
async def hierarchy(ctx):
    names = []
    counts = []  
    highest = 0    
    with open('milkNames.txt', 'r+', encoding='utf-8') as file:
        names = file.readlines()
    with open('milkCounts.txt', 'r+', encoding='utf-8') as file:
        counts = file.readlines()
    
    counts = sorted(int(counts))
    embedVar = discord.Embed(title="Text Commands", description="Command Prefix: ~", color=0xf900ff)
    for i, count in enumerate(counts):
        
        file.writelines(counts)
        embedVar.add_field(name="hey", value="return a random reply", inline=False)
    

def giveMilk(receiver, amount):
    names = []
    counts = []      
    with open('milkNames.txt', 'r+', encoding='utf-8') as file:
        names = file.readlines()
    with open('milkCounts.txt', 'r+', encoding='utf-8') as file:
        counts = file.readlines()                                                         
    lineIndex = -1
    for name in names:
        if str(name).strip() == receiver:
            lineIndex = names.index(name)
    if not lineIndex == -1:
        for i, line in enumerate(counts):
            if i == lineIndex:                                            
                if line.strip() == '':                                           
                    counts[lineIndex] = str(int(counts[lineIndex]) + amount)
                else:
                    counts[lineIndex] = str(int(counts[lineIndex]) + amount) + '\n'
                with open('milkCounts.txt', 'w') as file:
                    file.writelines(counts)
    else:
        nameFile = open('milkNames.txt', 'a', encoding='utf-8')
        countFile = open('milkCounts.txt', 'a', encoding='utf-8')
        nameFile.write('\n' + receiver)
        countFile.write('\n' + str(amount))

def takeMilk(receiver, amount):
    available = False
    if int(amount) > int(milkCount(str(receiver))):
        available = False
    else:
        available = True
        names = []
        counts = []      
        with open('milkNames.txt', 'r+', encoding='utf-8') as file:
            names = file.readlines()
        with open('milkCounts.txt', 'r+', encoding='utf-8') as file:
            counts = file.readlines()                                                         
        lineIndex = -1
        for name in names:
            if str(name).strip() == receiver:
                lineIndex = names.index(name)
        if not lineIndex == -1:
            for i, line in enumerate(counts):
                if i == lineIndex: 
                    if line.strip() == '':                                           
                        counts[lineIndex] = str(int(counts[lineIndex]) - amount)
                    else:
                        counts[lineIndex] = str(int(counts[lineIndex]) - amount) + '\n'
                    with open('milkCounts.txt', 'w') as file:
                        file.writelines(counts)
        else:
            nameFile = open('milkNames.txt', 'a')
            countFile = open('milkCounts.txt', 'a')
            nameFile.write('\n' + receiver)
            countFile.write('\n' + str(-amount))
    return available

async def send_dm(ctx, member: discord.Member, *, content):
    channel = await member.create_dm()
    await channel.send(embed=content)

def milkCount(user):
    names = []
    counts = []   
    number = 0   
    with open('milkNames.txt', 'r+', encoding='utf-8') as file:
        names = file.readlines()
    with open('milkCounts.txt', 'r+', encoding='utf-8') as file:
        counts = file.readlines()   
    index = -1                                                      
    for name in names:
        if str(name).strip() == user:
            index = names.index(name) 
            number = counts[index]
    return number

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

@expose.error
async def expose_error(ctx, error):
    if str(error) == "member is a required argument that is missing.":
        await ctx.reply('Tag someone to expose :rolling_eyes:')
    else:
        print(str(error))

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, discord.ext.commands.errors.CommandNotFound):
        await ctx.reply("I don't know that command")
    if str(error) == "member is a required argument that is missing.":
        None
    else:
        print(str(error))

@mute.error
async def mute_error(ctx, error):
    print(str(error))

@unmute.error
async def unmute_error(ctx, error):
    print(str(error))

@say.error
async def say_error(ctx, error):
    print(str(error))

@play.error
async def play_error(ctx, error):
    print(str(error))

@edited.error
async def edited_error(ctx, error):
    print(str(error))

@hentai.error
async def hentai_error(ctx, error):
    print(str(error))

@rps.error
async def rps_error(error):
    print(str(error))
bot.run(TOKEN)