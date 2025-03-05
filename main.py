KEY = 'DJ_DISCORD_TOKEN'

# Python
import os
import logging
import signal
import platform

logger = logging.getLogger("main")
logging.basicConfig(filename='bot.log', level=logging.INFO)

# Imports Discord
import discord
from discord import app_commands
from discord.ext import tasks

# Extras
from discord_control import DiscordControl
from youtube_client import YouTube, valid_url
from discord_buttons import PlayerButtons

import utils

display = None

def is_linux(): return "Linux" == platform.system()

if is_linux():
    from epd import EPD
    display = EPD()

# Token
TOKEN = os.getenv(KEY)
 
if not TOKEN: raise ValueError(f'Token do BOT não definido! Defina o token na variável de ambiente "{KEY}" para prosseguir com a execução.')

# Permissões do Discord
intents = discord.Intents.default()
intents.presences = True
intents.message_content = True
intents.messages = True
intents.members = True

# Classes
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)
discord_control = DiscordControl(client)

@tree.command(name='play', description='Tocar música a partir de um link')
@app_commands.describe(url="URL do YouTube ou outra plataforma para tocar")
async def play_command(interaction: discord.Interaction, url: str):
    
    global player_buttons
    
    if await utils.validate_interaction(interaction):
        show_user_command(interaction)
        if not valid_url(url):
            await interaction.followup.send("❌ URL inválida!")
            return
        
        title = await discord_control.play(interaction.guild, interaction.user.voice.channel, url)
        
        if title: embed = utils.embed_message(description="💿 Tocando agora!", name=title, value=url)
        else: embed = utils.embed_message(description="💿 Colocando em fila...", name=YouTube(url).title(), value=url)
        
        await interaction.followup.send(embed=embed, view=PlayerButtons(discord_control))
        
@tree.command(name='queue', description='Exibir fila de reprodução')
async def queue_commnand(interaction: discord.Interaction):
    if await utils.validate_interaction(interaction):
        show_user_command(interaction)
        await discord_control.show_queue(interaction)

@tree.command(name='clear', description='Limpar fila de reprodução')
async def queue_commnand(interaction: discord.Interaction):
    if await utils.validate_interaction(interaction):
        show_user_command(interaction)
        discord_control.clear_queue(interaction.guild)
        await interaction.followup.send("🗑️ Tudo limpo!")

@tree.command(name='pause', description='Pausar a reprodução')
async def pause_command(interaction: discord.Interaction):
    if await utils.validate_interaction(interaction):
        show_user_command(interaction)
        discord_control.pause(interaction.guild)
        await interaction.followup.send("⏸️ Pausado!")

@tree.command(name='resume', description='Continuar a reprodução')
async def resume_command(interaction: discord.Interaction):
    if await utils.validate_interaction(interaction):
        show_user_command(interaction)
        discord_control.resume(interaction.guild)
        await interaction.followup.send("▶️ Continuando...")

@tree.command(name='stop', description='Parar a reprodução')
async def stop_command(interaction: discord.Interaction):
    if await utils.validate_interaction(interaction):
        show_user_command(interaction)
        discord_control.stop(interaction.guild)
        await interaction.followup.send("⏹️ Para tudo!")

@tree.command(name='join', description='Vou me juntar a você!')
async def join_command(interaction: discord.Interaction):
    if await utils.validate_interaction(interaction):
        show_user_command(interaction)
        await discord_control.join(interaction.guild, interaction.user.voice.channel)
        await interaction.followup.send("🤠 Opa, bão!?")

@tree.command(name='leave', description='Sairei do canal de voz')
async def leave_command(interaction: discord.Interaction):
    if await utils.validate_interaction(interaction):
        show_user_command(interaction)
        await discord_control.leave(interaction.guild)
        await interaction.followup.send("🫡 Estarei à disposição!")

@tree.command(name='skip', description='Pular para a próxima música')
async def skip_command(interaction: discord.Interaction):
    if await utils.validate_interaction(interaction):
        show_user_command(interaction)
        discord_control.skip(interaction.guild)
        await interaction.followup.send("⏭️ Pulando!")   

@tree.command(name='help', description='Exibir opções de comando')
async def help_command(interaction: discord.Interaction):
    if await utils.validate_interaction(interaction):
        show_user_command(interaction)
        msg = "**/play [URL]** - Tocar música a partir de um link\n"
        
        msg += "**/pause** - Pausar a reprodução\n"
        msg += "**/resume** - Continuar a reprodução\n"
        msg += "**/skip** - Pular para a próxima música\n"
        msg += "**/stop** - Parar a reprodução\n"
        msg += "**/join** - Juntar-se ao canal de voz\n"
        msg += "**/leave** - Sair do canal de voz\n"
        msg += "**/queue** - Exibir fila de reprodução\n"
        msg += "**/clear** - Limpar fila de reprodução\n"
        msg += "**/help** - Exibir opções de comando (esta mensagem)\n\n"
        
        msg += "DJ Marquinhos criado por <@189162346063593473>"
        
        await interaction.followup.send(embed=utils.embed_message(description="📚 Comandos disponíveis", name="Lista", value=msg), ephemeral=True)

@client.event
async def on_connect():
    background_task.start()

@client.event
async def on_ready():
    await tree.sync()
    logger.info(f'Entrei como {client.user}')

def show_user_command(interaction: discord.Interaction):
    if is_linux():
        user = interaction.user.name
        command = interaction.command.name
        display.command(user, command)

def signal_handler(sig, frame):
    if is_linux(): display.clear()
    client.close()
    raise SystemExit("Encerrando BOT...")
    
signal.signal(signal.SIGTERM, signal_handler)

@tasks.loop(seconds = 5)
async def background_task():
    if is_linux():
        display.plot()
        display.channels(discord_control.connections_count())

if is_linux(): display.splash()

client.run(TOKEN)