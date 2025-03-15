KEY = 'DJ_DISCORD_TOKEN'

# Python
import os
import logging
import signal
import asyncio
import multiprocessing

# Imports Discord
import discord
from discord import app_commands, WebhookMessage, Message, File
from discord.ext import tasks

# Extras
import utils

from discord_controller import DiscordController
from discord_buttons import DiscordButtons

from mp3_platform import MP3Platform
from youtube_platform import YouTubePlatform

from sound_platform import PlatformHandler, SoundPlatformException

BACKGROUND_TASK_INTERVAL = 2

TOKEN = utils.token_arg() or os.getenv(KEY)

if not TOKEN: raise ValueError(f'Token do BOT não definido! Defina o token na variável de ambiente "{KEY}" para prosseguir com a execução.')

# Discord intents
intents = discord.Intents.default()
intents.presences = True
intents.message_content = True
intents.messages = True
intents.members = True

client = discord.Client(intents=intents)

# Classes
tree = app_commands.CommandTree(client)
controller = DiscordController()

buttons = None  

# Logger
logger = logging.getLogger(__name__)
logging.basicConfig(filename='dj-marquinhos.log', level=logging.INFO)

def get_buttons():
    global buttons
    if buttons is None:
        buttons = DiscordButtons(controller)
        client.add_view(buttons)

    return buttons

async def interaction_play(interaction: discord.Interaction, url: str):
    try:
        msg: WebhookMessage = await interaction.followup.send("💿 Carregando sua música...")
        
        title = await controller.play(interaction, url)
        if title:
            await msg.edit(content=None, embed=utils.embed_message(description="💿 Tocando agora!", name=title, value=url), view=get_buttons())
        else:
            await msg.edit(content="💿 Colocando em fila...")
            await msg.delete(delay=5)
            multiprocessing.Process(target=controller.process_queue).start()
            
            

    except SoundPlatformException as e:
        logger.error(e)
        await interaction.followup.send(str(e))
    except Exception as e:
        logger.error(e)
        await interaction.followup.send("Erro inesperado: {err}".format(err=str(e).lower()))

async def message_play(message: discord.Message, url: str):
    try:
        msg: Message = await message.reply("💿 Carregando sua música...")
        
        title = await controller.play(message.guild, message.author.voice.channel, url)
        
        if title:
            await msg.edit(content=None, embed=utils.embed_message(description="💿 Tocando agora!", name=title, value=url), view=get_buttons())
        else:
            await msg.edit("💿 Colocando em fila...")
            await msg.delete(delay=5)
            multiprocessing.Process(target=controller.process_queue).start()

    except SoundPlatformException as e:
        logger.error(e)
        await message.reply(str(e))
    except Exception as e:
        logger.error(e)
        await message.reply("Erro inesperado: {err}".format(err=str(e).lower()))

@tree.command(name='play', description="Tocar música a partir de um link")
@app_commands.describe(url="URL do YouTube ou outra plataforma para tocar")
async def play_command(interaction: discord.Interaction, url: str):
    if await utils.validate_interaction(interaction):
        if not PlatformHandler.valid_url(url):
            await interaction.followup.send("❌ URL inválida!")
            return
        
        await asyncio.create_task(interaction_play(interaction, url))
        
@client.event
async def on_message(message: discord.Message):
    if message.author == client.user: return
    
    if await utils.validate_message(message):
        if client.user.mentioned_in(message):
            msg = message.content
            if "play" in msg:
                if len(message.attachments) > 0:
                    attachment = message.attachments[0]
                    url = attachment.url
                    if not PlatformHandler.valid_url(url):
                        await message.reply("❌ URL inválida!")
                        return
                    await asyncio.create_task(message_play(message, url))
                else:
                    mp3_link = MP3Platform.extract_mp3_url(msg)
                    if not mp3_link: await message.reply("🐻 Opa, bão!?")
                    else: await asyncio.create_task(message_play(message, mp3_link))

@tree.command(name='queue', description="Exibir fila de reprodução")
async def queue_command(interaction: discord.Interaction):
    if await utils.validate_interaction(interaction):
        await controller.show_queue(interaction)
        
@tree.command(name='pix', description="Exibir o QR Code do PIX")
async def pix_command(interaction: discord.Interaction):
    await interaction.response.defer()
    
    image = File("./pix.png")
    embed = discord.Embed(title="PIX para doação", description="☕ Me compre um café...\n...está **muito** caro!", color=0x993399)
    embed.set_image(url="attachment://pix.png")
    embed.set_footer(text="O desenvolvedor agradece!")
    msg: WebhookMessage = await interaction.followup.send(embed=embed, file=image)
    
    await msg.delete(delay=60)

@tree.command(name='clear', description="Limpar fila de reprodução")
async def clear_command(interaction: discord.Interaction):
    if await utils.validate_interaction(interaction):
        controller.clear_queue(interaction.guild)
        await interaction.followup.send("🗑️ Tudo limpo!")

@tree.command(name='pause', description="Pausar a reprodução")
async def pause_command(interaction: discord.Interaction):
    if await utils.validate_interaction(interaction):
        controller.pause(interaction.guild)
        await interaction.followup.send("⏸️ Pausado!")

@tree.command(name='resume', description="Continuar a reprodução")
async def resume_command(interaction: discord.Interaction):
    if await utils.validate_interaction(interaction):
        controller.resume(interaction.guild)
        await interaction.followup.send("▶️ Continuando...")

@tree.command(name='stop', description="Parar a reprodução")
async def stop_command(interaction: discord.Interaction):
    if await utils.validate_interaction(interaction):
        controller.stop(interaction.guild)
        await interaction.followup.send("⏹️ Para tudo!")
        
@tree.command(name='keep', description="Manter-se no canal")
async def keep_command(interaction: discord.Interaction):
    if await utils.validate_interaction(interaction):
        keep = controller.keep(interaction.guild)
        
        if keep is not None:
            if keep: await interaction.followup.send("😎 Vou ficar, com certeza!")
            else: await interaction.followup.send("🫡 Vou sair no momento certo!")

@tree.command(name='join', description="Vou me juntar a você!")
async def join_command(interaction: discord.Interaction):
    if await utils.validate_interaction(interaction):
        await controller.join(interaction, play_intro=True)
        
@tree.command(name='leave', description="Sairei do canal de voz")
async def leave_command(interaction: discord.Interaction):
    if await utils.validate_interaction(interaction):
        await controller.leave(interaction)
        await interaction.followup.send("🫡 Estarei à disposição!")

@tree.command(name='skip', description="Pular para a próxima música")
async def skip_command(interaction: discord.Interaction):
    if await utils.validate_interaction(interaction):
        controller.skip(interaction.guild)
        await interaction.followup.send("⏭️ Pulando!")   

@tree.command(name='help', description="Exibir opções de comando")
async def help_command(interaction: discord.Interaction):
    if await utils.validate_interaction(interaction):
        
        msg = "**/play [URL]** - Tocar música a partir de um link\n"
        msg += "**/pause** - Pausar a reprodução\n"
        msg += "**/resume** - Continuar a reprodução\n"
        msg += "**/skip** - Pular para a próxima música\n"
        msg += "**/stop** - Parar a reprodução\n"
        msg += "**/join** - Juntar-se ao canal de voz\n"
        msg += "**/leave** - Sair do canal de voz\n"
        msg += "**/keep** - Ficar ou não ficar no canal\n"
        msg += "**/queue** - Exibir fila de reprodução\n"
        msg += "**/clear** - Limpar fila de reprodução\n"
        msg += "**/pix** - **Já sabe, né?**\n"
        msg += "**/help** - Exibir opções de comando (esta mensagem)\n\n"
        
        msg += "DJ Marquinhos criado por <@189162346063593473>"
        
        await interaction.followup.send(embed=utils.embed_message(description="📚 Comandos disponíveis", name="Lista", value=msg), ephemeral=True)

@client.event
async def on_app_command_completion(interaction: discord.Interaction, command: discord.app_commands.Command):
    username = interaction.user.name
    user_id = interaction.user.id
    command_name = command.name
    
    logger.info(f"[{user_id}] {username} usou /{command_name}")

@tasks.loop(seconds = BACKGROUND_TASK_INTERVAL)
async def background_task():
    await controller.clean()

@client.event
async def on_connect():
    background_task.start()

@client.event
async def on_ready():
    await tree.sync()
    logger.info(f"Entrei como {client.user.name}")
    await client.change_presence(status=discord.Status.online, activity=discord.Streaming(name='/join', url="https://www.devclub.dev.br/dj-marquinhos"))


def signal_handler(sig, frame):
    client.close()
    raise SystemExit("Encerrando BOT...")

if __name__ == "__main__":
    PlatformHandler.show_classes()
    
    signal.signal(signal.SIGTERM, signal_handler)
    client.run(TOKEN)