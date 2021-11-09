import discord
from discord.ext import commands
from discord.utils import get
from discord import FFmpegPCMAudio
from youtube_dl import YoutubeDL
import asyncio

from youtube_dl.utils import DownloadError

client = commands.Bot(command_prefix="+")
queues = {}
timeout = 300.0 # seconds

def create_new_player(url : str):
    YDL_OPTIONS = {
        'format': 'bestaudio', 
        'noplaylist':'True',
        'default_search': 'auto'
    }

    FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}

    with YoutubeDL(YDL_OPTIONS) as ydl:
        info = ydl.extract_info(url, download=False)

    if "entries" in info:
        # print(info)
        info = info["entries"][0]

    URL = info['formats'][0]['url']
    title = info["title"]
    # print(title)

    return {"title":title, "player":FFmpegPCMAudio(URL, **FFMPEG_OPTIONS)}

async def loop_queue(ctx : commands.Context):
    """Checks the queue and starts the next song in the bot in the guild of the context."""
    queue = queues[ctx.guild.id]
    voice_client : discord.VoiceClient = get(client.voice_clients, guild=ctx.guild)
    next = asyncio.Event()

    now_playing : discord.Message = None
    player = None
    while True:
    # while queue.qsize() != 0:
        queue = queues[ctx.guild.id]
        next.clear()

        try:
            title_player_dict = await asyncio.wait_for(
                queue.get(),
                timeout=timeout,
            )
        except asyncio.TimeoutError:
            print("timeout")
            await change_status("paint dry")
            await leave(ctx)
            break

        if now_playing is not None:
            try:
                await now_playing.delete()
            except discord.HTTPException:
                pass

        # await send_message(ctx, f"Now playing {next_url}")
        # title_player_dict = create_new_player(next_url)
        title = title_player_dict["title"]
        player = title_player_dict["player"]

        now_playing = await ctx.send(f"Now playing {title}")
        await change_status(title)

        voice_client.play(player, after=lambda _: client.loop.call_soon_threadsafe(next.set))

        await next.wait()
        player.cleanup()

async def send_message(ctx : commands.Context, msg):
    await ctx.send(msg)

async def change_status(new_status : str):
    await client.change_presence(
        status=discord.Status.online, 
        activity = discord.Activity(type=discord.ActivityType.listening, name=new_status)
    )

@client.event
async def on_ready():
    print(f"Logged in as {client.user}")
    await change_status("paint dry")

# @client.command(pass_context = True)
async def join(ctx):
    channel = ctx.message.author.voice.channel
    await channel.connect()

@client.command(pass_context = True)
async def leave(ctx):
    voice_client = get(client.voice_clients, guild=ctx.guild)
    await voice_client.disconnect()
    queues.pop(ctx.guild.id)

@client.command(pass_context = True)
async def play(ctx, *url_words):
    url = " ".join(url_words)
    guild = ctx.guild
    voice_client : discord.VoiceClient = get(client.voice_clients, guild=guild)
    
    if voice_client is None:
        await join(ctx)
        voice_client : discord.VoiceClient = get(client.voice_clients, guild=guild)


    new_queue = False
    if guild.id not in queues:
        queues[guild.id] = asyncio.Queue()
        new_queue = True

    queue = queues[guild.id]

    try:
        await queue.put(create_new_player(url))
    except DownloadError:
        await ctx.send(f"Could not play {url}. Unsupported URL.")
    # await queue.put(url)

    # if not voice_client.is_playing():
    if new_queue:
        voice_client.loop.create_task(loop_queue(ctx))
    elif voice_client.is_playing():
        await ctx.send(f"Adding {url} to the queue. It is number {queue.qsize()} in queue.")

@client.command(pass_context = True)
async def stop(ctx):
    guild = ctx.guild
    if guild.id in queues:
        queues[guild.id] = asyncio.Queue()

    voice_client = get(client.voice_clients, guild=guild)
    voice_client.stop()

@client.command()
async def pause(ctx):
    voice_client = get(client.voice_clients, guild=ctx.guild)
    voice_client.pause()

@client.command()
async def resume(ctx):
    voice_client = get(client.voice_clients, guild=ctx.guild)
    voice_client.resume()

@client.command()
async def skip(ctx):
    voice_client : discord.VoiceClient = get(client.voice_clients, guild=ctx.guild)
    if voice_client.is_playing():
        voice_client.stop()
    # voice_client.loop.create_task(loop_queue(ctx))


# Can change this to the bot token
bot_token = None

# Or store the token in a file called keys in folder secret
if bot_token is None:
    with open("keys") as f:
        for line in f.readlines():
            if line.split("=")[0] == "BOT_TOKEN":
                bot_token = line.split("=")[1]

client.run(bot_token)
