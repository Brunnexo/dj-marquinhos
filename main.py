KEY = 'DJ_DISCORD_TOKEN'

# Python
import os
import logging
import signal
import asyncio
import multiprocessing
from datetime import datetime

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

async def temp_webhook_message(interaction: discord.Interaction, embed = None, content: str = None, delay = 10):
    msg: WebhookMessage = await interaction.followup.send(content=content, embed=embed)
    await msg.delete(delay=delay)

async def temp_message_reply(message: discord.Message, embed = None, content = None, delay = 10):
    msg: Message = await message.reply(content=content, embed=embed)
    await msg.delete(delay=delay)

async def interaction_play(interaction: discord.Interaction, url: str):
    try:
        msg: WebhookMessage = await interaction.followup.send("💿 Carregando sua música...")
        
        title = await controller.interaction_play(interaction, url)
        
        if title:
            await msg.edit(content=None, embed=utils.embed_message(description="💿 Tocando agora!", name=title, value=url), view=get_buttons())
        else:
            await msg.edit(content="💿 Colocando em fila...")
            multiprocessing.Process(target=controller.process_queue).start()
            await msg.delete(delay=5)

    except SoundPlatformException as e:
        logger.error(e)
        await interaction.followup.send(str(e))
    except Exception as e:
        logger.error(e)
        await interaction.followup.send("Erro inesperado: {err}".format(err=str(e).lower()))

async def message_play(message: discord.Message, url: str):
    try:
        msg: Message = await message.reply("💿 Carregando sua música...")
        title = await controller.message_play(message, url)
        if title:
            await msg.edit(content=None, embed=utils.embed_message(description="💿 Tocando agora!", name=title, value=url), view=get_buttons())
        else:
            await msg.edit("💿 Colocando em fila...")
            multiprocessing.Process(target=controller.process_queue).start()
            await msg.delete(delay=5)
    except SoundPlatformException as e:
        logger.error(e)
        await temp_message_reply(message, content="**Erro na plataforma:\n{err}**".format(err=str(e)))
    except Exception as e:
        logger.error(e)
        await temp_message_reply(message, content="**Erro inesperado:\n{err}**".format(err=str(e)))

@tree.command(name='play', description="Tocar música a partir de um link")
@app_commands.describe(url="URL do YouTube ou outra plataforma para tocar")
async def play_command(interaction: discord.Interaction, url: str):
    if await utils.validate_interaction(interaction):
        if not PlatformHandler.valid_url(url):
            await temp_webhook_message(interaction, content="URL **inválida**!\nVocê colocou \"**{url}**\" no campo.\n*Está literalmente escrito **URL** no campo!*\n[Clique aqui para aprender sobre URLs](https://pt.wikipedia.org/wiki/URL)".format(url=url), delay=60)
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
                    await asyncio.create_task(controller.message_play(message, url))
                else:
                    mp3_link = MP3Platform.extract_mp3_url(msg)
                    if not mp3_link: await message.reply("🐻 Opa, bão!?")
                    else: await asyncio.create_task(controller.message_play(message, mp3_link))

@tree.command(name='queue', description="Exibir fila de reprodução")
async def queue_command(interaction: discord.Interaction):
    if await utils.validate_interaction(interaction):
        await controller.show_queue(interaction)
        
@tree.command(name='pix', description="Exibir o QR Code do PIX")
async def pix_command(interaction: discord.Interaction):
    if await utils.validate_interaction(interaction):
        image = File("./pix.png")
        embed = discord.Embed(title="PIX para doação", description="☕ Me compre um café...\n...está **muito** caro!", color=0x993399)
        embed.set_image(url="attachment://pix.png")
        embed.set_footer(text="O desenvolvedor agradece!")
        
        msg: WebhookMessage = await interaction.followup.send(embed=embed, file=image)
        
        await msg.delete(delay=120)

@tree.command(name='clear', description="Limpar fila de reprodução")
async def clear_command(interaction: discord.Interaction):
    if await utils.validate_interaction(interaction):
        controller.clear_queue(interaction.guild)
        await temp_webhook_message(interaction, content="🗑️ Tudo limpo!", delay=5)

@tree.command(name='pause', description="Pausar a reprodução")
async def pause_command(interaction: discord.Interaction):
    if await utils.validate_interaction(interaction):
        controller.pause(interaction.guild)
        await temp_webhook_message(interaction, content="⏸️ Pausado!", delay=5)

@tree.command(name='resume', description="Continuar a reprodução")
async def resume_command(interaction: discord.Interaction):
    if await utils.validate_interaction(interaction):
        controller.resume(interaction.guild)
        await temp_webhook_message(interaction, content="▶️ Continuando...", delay=5)

@tree.command(name='stop', description="Parar a reprodução")
async def stop_command(interaction: discord.Interaction):
    if await utils.validate_interaction(interaction):
        controller.stop(interaction.guild)
        await temp_webhook_message(interaction, content="⏹️ Para tudo!", delay=5)
        
@tree.command(name='keep', description="Manter-se no canal")
async def keep_command(interaction: discord.Interaction):
    if await utils.validate_interaction(interaction):
        keep = controller.keep(interaction.guild)
        
        if keep is not None:
            if keep: await temp_webhook_message(interaction, content="😎 Vou ficar, com certeza!", delay=5)
            else: await temp_webhook_message(interaction, content="🫡 Vou sair no momento certo!", delay=5)

@tree.command(name='join', description="Vou me juntar a você!")
async def join_command(interaction: discord.Interaction):
    if await utils.validate_interaction(interaction):
        await controller.interaction_join(interaction, play_intro=True)
        await temp_webhook_message(interaction, content="🐻 Opa, bão!?", delay=10)
        
@tree.command(name='leave', description="Sairei do canal de voz")
async def leave_command(interaction: discord.Interaction):
    if await utils.validate_interaction(interaction):
        await controller.leave(interaction)
        await temp_webhook_message(interaction, content="🫡 Estarei à disposição!", delay=10)

@tree.command(name='skip', description="Pular para a próxima música")
async def skip_command(interaction: discord.Interaction):
    if await utils.validate_interaction(interaction):
        controller.skip(interaction.guild)
        await temp_webhook_message(interaction, content="⏭️ Pulando!", delay=10)

@tree.command(name='help', description="Exibir opções de comando")
async def help_command(interaction: discord.Interaction):
    if await utils.validate_interaction(interaction):
        
        reply = "**/play [URL]** - Tocar música a partir de um link\n"
        reply += "**/pause** - Pausar a reprodução\n"
        reply += "**/resume** - Continuar a reprodução\n"
        reply += "**/skip** - Pular para a próxima música\n"
        reply += "**/stop** - Parar a reprodução\n"
        reply += "**/join** - Juntar-se ao canal de voz\n"
        reply += "**/leave** - Sair do canal de voz\n"
        reply += "**/keep** - Ficar ou não ficar no canal\n"
        reply += "**/queue** - Exibir fila de reprodução\n"
        reply += "**/clear** - Limpar fila de reprodução\n"
        reply += "**/pix** - *Já sabe, né?*\n"
        reply += "**/help** - Exibir opções de comando (esta mensagem)\n\n"
        
        reply += "DJ Marquinhos criado por <@189162346063593473>"
        
        await temp_webhook_message(interaction, embed=utils.embed_message(description="📚 Comandos disponíveis", name="Lista", value=reply), delay=60)

@client.event
async def on_app_command_completion(interaction: discord.Interaction, command: discord.app_commands.Command):
    username = interaction.user.name
    user_id = interaction.user.id
    command_name = command.name
    
    logger.info(f"[{user_id}] {username} usou /{command_name}")

def clear_cache():
    get_youtube_obj_cache = YouTubePlatform.get_youtube_obj.cache_info()
    get_stream_url_cache = YouTubePlatform.get_stream_url.cache_info()

    if get_youtube_obj_cache.currsize > 0 or get_stream_url_cache.currsize > 0:
        logger.setLevel(logging.DEBUG)
        
        logger.debug("Informações do cache:")
        
        logger.debug(f"YouTubePlatform::get_youtube_obj - caches salvos: {get_youtube_obj_cache.currsize}")
        logger.debug("Limpando cache YouTubePlatform::get_youtube_obj...")
        YouTubePlatform.get_youtube_obj.cache_clear()
        
        logger.debug(f"YouTubePlatform::get_stream_url - caches salvos: {get_stream_url_cache.currsize}")
        logger.debug("Limpando cache YouTubePlatform::get_stream_url...")
        YouTubePlatform.get_stream_url.cache_clear()
        
        logger.setLevel(logging.INFO)

@tasks.loop(seconds = BACKGROUND_TASK_INTERVAL)
async def background_task():
    await controller.clean()
    now = datetime.now()
    if now.hour == 0 and now.minute == 0: clear_cache()

@client.event
async def on_connect():
    background_task.start()

@client.event
async def on_ready():
    await tree.sync()
    logger.info(f"Entrei como {client.user.name}")
    await asyncio.sleep(10)
    await client.change_presence(status=discord.Status.online, activity=discord.CustomActivity(name='/help'))


def signal_handler(sig, frame):
    client.close()
    raise SystemExit("Encerrando BOT...")

if __name__ == "__main__":
    PlatformHandler.show_classes()
    
    signal.signal(signal.SIGTERM, signal_handler)
    client.run(TOKEN)