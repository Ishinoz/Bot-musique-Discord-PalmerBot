import discord
import os
import asyncio
from dotenv import load_dotenv
from discord.ext import commands
from discord import app_commands
import yt_dlp


load_dotenv()

FFMPEG_PATH = r"C:\Users\Yann Loic\Documents\ffmpeg-2026-06-15-git-44d082edc8-essentials_build\bin\ffmpeg.exe"


intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)

KK

queues = {}

ydl_opts = {
    "format": "bestaudio/best",
    "noplaylist": True
}



async def search_ytdlp_async(query, ydl_opts):
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(None, lambda: _extract(query, ydl_opts))


def _extract(query, ydl_opts):
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        return ydl.extract_info(query, download=False)



async def play_next(guild, voice_client):

    guild_id = guild.id

    if guild_id not in queues or not queues[guild_id]:
        return

    audio_url, title = queues[guild_id].pop(0)

    ffmpeg_options = {
        "before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5",
        "options": "-vn"
    }

    source = discord.FFmpegPCMAudio(
        audio_url,
        executable=FFMPEG_PATH,
        **ffmpeg_options
    )

    def after_playing(error):
        fut = asyncio.run_coroutine_threadsafe(
            play_next(guild, voice_client),
            bot.loop
        )
        try:
            fut.result()
        except:
            pass

    voice_client.play(source, after=after_playing)



@bot.event
async def on_ready():
    await bot.tree.sync()
    print("Bot prêt !")



@bot.tree.command(name="play")
async def play(interaction: discord.Interaction, song_query: str):

    await interaction.response.defer()

    
    if interaction.user.voice is None:
        await interaction.followup.send("❌ Tu dois être dans un vocal.")
        return

    voice_channel = interaction.user.voice.channel
    voice_client = interaction.guild.voice_client

  
    if voice_client is None:
        voice_client = await voice_channel.connect()
    elif voice_client.channel != voice_channel:
        await voice_client.move_to(voice_channel)

    
    ydl_opts = {
        "format": "bestaudio/best",
        "noplaylist": True,
        "cookiefile": "www.youtube.com_cookies.txt",
        "quiet": True,
        "extractor_args": {
            "youtube": {
                "player_client": ["android", "web"]
            }
        },
        "http_headers": {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
        }
    }

  
    is_url = song_query.startswith("http")

   
    if is_url:

        results = await search_ytdlp_async(song_query, ydl_opts)
        track = results

   
    else:

        results = await search_ytdlp_async(f"ytsearch:{song_query}", ydl_opts)

        entries = results.get("entries") or []

        if not entries:
            await interaction.followup.send("❌ Aucun résultat trouvé.")
            return

        track = entries[0]

    
    audio_url = track.get("url")

    if not audio_url:
        await interaction.followup.send("❌ Impossible de récupérer l’audio.")
        return

    title = track.get("title", "Unknown")

    
    guild_id = interaction.guild.id

    if guild_id not in queues:
        queues[guild_id] = []

    queues[guild_id].append((audio_url, title))

    await interaction.followup.send(f"➕ Ajouté : **{title}**")

    
    if not voice_client.is_playing():
        await play_next(interaction.guild, voice_client)



@bot.tree.command(name="skip")
async def skip(interaction: discord.Interaction):

    vc = interaction.guild.voice_client

    if vc and vc.is_playing():
        vc.stop()
        await interaction.response.send_message("⏭️ Skip !")
    else:
        await interaction.response.send_message("Rien à skip.")



@bot.tree.command(name="stop")
async def stop(interaction: discord.Interaction):

    vc = interaction.guild.voice_client

    if vc:
        queues[interaction.guild.id] = []
        await vc.disconnect()
        await interaction.response.send_message("🛑 Stop + déconnexion")
    else:
        await interaction.response.send_message("Je ne suis pas connecté.")



@bot.tree.command(name="pause")
async def pause(interaction: discord.Interaction):

    vc = interaction.guild.voice_client

    if vc and vc.is_playing():
        vc.pause()
        await interaction.response.send_message("⏸️ Pause")
    else:
        await interaction.response.send_message("Rien à mettre en pause.")



@bot.tree.command(name="resume")
async def resume(interaction: discord.Interaction):

    vc = interaction.guild.voice_client

    if vc and vc.is_paused():
        vc.resume()
        await interaction.response.send_message("▶️ Reprise")
    else:
        await interaction.response.send_message("Rien à reprendre.")



bot.run(os.getenv("DISCORD_TOKEN"))