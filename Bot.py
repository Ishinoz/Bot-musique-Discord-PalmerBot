import discord
import os
from dotenv import load_dotenv
from discord.ext import commands
load_dotenv()

print("Lancement de PalmerBot")
bot = commands.Bot(command_prefix="/", intents=discord.Intents.all())

@bot.event
async def on_ready():
    # Synchroniser les commandes
    try:
        synced  = await bot.tree.sync()
        print(f"Commandes slash synchronisées : {len(synced)}")
    except Exception as e:
        print(e)

    print(" PalmerBot Prêt ! ")

@bot.event
async def on_message(message= discord.Message):

    if message.author.bot:
        return

    if message.content.lower() == 'bonjour':
        channel = message.channel
        await channel.send("ça gaze ?")
    if message.content.lower() == 'ça va pi toi':
        channel = message.channel
        await channel.send("Au Top !")

@bot.tree.command(name="youtube", description="Affiche ma chaine youtube")
async def youtube(interaction: discord.Interaction):
    await interaction.response.send_message("Voici le lien de ma chaine : https://www.youtube.com/@Ishinoz ")

bot.run(os.getenv('DISCORD_TOKEN'))