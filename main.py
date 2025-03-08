KEY = 'DJ_DISCORD_TOKEN'

# Python
import os
import logging
import signal

# Imports Discord
import discord
from discord import app_commands
from discord.ext import tasks

# Extras
import strings
import utils

from discord_controller import DiscordController
from discord_buttons import DiscordButtons

from mp3_platform import MP3Platform
from youtube_platform import YouTubePlatform

from sound_platform import PlatformHandler, SoundPlatformException

# Token
TOKEN = os.getenv(KEY)

if not TOKEN: raise ValueError(strings.ERR_TOKEN.format(KEY=KEY))

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
        title = await controller.play(interaction.guild, interaction.user.voice.channel, url)
        
        if title: embed = utils.embed_message(description=strings.STR_PLAY_NOW_PLAYING, name=title, value=url)
        else: embed = utils.embed_message(description=strings.STR_PLAY_QUEUEING, name=PlatformHandler(url).title(), value=url)
        
        await interaction.followup.send(embed=embed, view=get_buttons())
    except SoundPlatformException as e:
        await interaction.followup.send(str(e))
    except Exception as e:
        await interaction.followup.send(strings.ERR_EXCEPTION_GENERIC.format(err=str(e).lower()))

@tree.command(name='play', description=strings.STR_PLAY_CMD_DESC)
@app_commands.describe(url=strings.STR_PLAY_URL_DESC)
async def play_command(interaction: discord.Interaction, url: str):
    if await utils.validate_interaction(interaction):
        if not PlatformHandler.valid_url(url):
            await interaction.followup.send(strings.ERR_INVALID_URL)
            return
        
        await interaction_play(interaction, url)

        
@tree.command(name='queue', description=strings.STR_QUEUE_CMD_DESC)
async def queue_command(interaction: discord.Interaction):
    if await utils.validate_interaction(interaction):
        await controller.show_queue(interaction)

@tree.command(name='clear', description=strings.STR_CLEAR_CMD_DESC)
async def clear_command(interaction: discord.Interaction):
    if await utils.validate_interaction(interaction):
        controller.clear_queue(interaction.guild)
        await interaction.followup.send(strings.STR_CLEAR_REPLY)

@tree.command(name='pause', description=strings.STR_PAUSE_CMD_DESC)
async def pause_command(interaction: discord.Interaction):
    if await utils.validate_interaction(interaction):
        controller.pause(interaction.guild)
        await interaction.followup.send(strings.STR_PAUSE_REPLY)

@tree.command(name='resume', description=strings.STR_RESUME_CMD_DESC)
async def resume_command(interaction: discord.Interaction):
    if await utils.validate_interaction(interaction):
        controller.resume(interaction.guild)
        await interaction.followup.send(strings.STR_RESUME_REPLY)

@tree.command(name='stop', description=strings.STR_STOP_CMD_DESC)
async def stop_command(interaction: discord.Interaction):
    if await utils.validate_interaction(interaction):
        controller.stop(interaction.guild)
        await interaction.followup.send(strings.STR_STOP_REPLY)

@tree.command(name='join', description=strings.STR_JOIN_CMD_DESC)
async def join_command(interaction: discord.Interaction):
    if await utils.validate_interaction(interaction):
        await controller.join(interaction.guild, interaction.user.voice.channel)
        await interaction.followup.send(strings.STR_JOIN_REPLY)

@tree.command(name='leave', description=strings.STR_LEAVE_CMD_DESC)
async def leave_command(interaction: discord.Interaction):
    if await utils.validate_interaction(interaction):
        await controller.leave(interaction.guild)
        await interaction.followup.send(strings.STR_LEAVE_REPLY)

@tree.command(name='skip', description=strings.STR_SKIP_CMD_DESC)
async def skip_command(interaction: discord.Interaction):
    if await utils.validate_interaction(interaction):
        controller.skip(interaction.guild)
        await interaction.followup.send(strings.STR_SKIP_REPLY)   

@tree.command(name='help', description=strings.STR_HELP_CMD_DESC)
async def help_command(interaction: discord.Interaction):
    if await utils.validate_interaction(interaction):
        await interaction.followup.send(embed=utils.embed_message(description=strings.STR_HELP_AVAIL_CMDS, name=strings.STR_HELP_LIST, value=strings.STR_HELP_MSG), ephemeral=True)

@client.event
async def on_app_command_completion(interaction: discord.Interaction, command: discord.app_commands.Command):
    print(interaction.user.name)
    print(command.name)

async def message_play(message: discord.Message, url: str):
    try:
        title = await controller.play(message.guild, message.author.voice.channel, url)
        
        if title: embed = utils.embed_message(description=strings.STR_PLAY_NOW_PLAYING, name=title, value=url)
        else: embed = utils.embed_message(description=strings.STR_PLAY_QUEUEING, name=PlatformHandler(url).title(), value=url)
        
        await message.reply(embed=embed, view=get_buttons())
    except SoundPlatformException as e:
        await message.reply(str(e))
    except Exception as e:
        await message.reply(strings.ERR_EXCEPTION_GENERIC.format(err=str(e).lower()))

@client.event
async def on_message(message: discord.Message):
    if message.author == client.user:
        return
    
    if await utils.validate_message(message):
        if client.user.mentioned_in(message):
            msg = message.content
            
            if "play" in msg:
                if len(message.attachments) > 0:
                    attachment = message.attachments[0]
                    url = attachment.url
                    
                    if not PlatformHandler.valid_url(url):
                        await message.reply(strings.ERR_INVALID_URL)
                        return
                    
                    await message_play(message, url)
                else:
                    mp3_link = utils.extract_mp3_url(msg)
                    
                    if not mp3_link:
                        await message.reply(strings.STR_JOIN_REPLY)
                    else:
                        await message_play(message, mp3_link)
                        
                        
        
@tasks.loop(seconds = 5)
async def background_task():
    pass

@client.event
async def on_connect():
    background_task.start()

@client.event
async def on_ready():
    await tree.sync()
    logger.info(strings.STR_ETC_LOGIN.format(user=client.user.name))

def signal_handler(sig, frame):
    client.close()
    raise SystemExit(strings.STR_ETC_CLOSING)


PlatformHandler.show_classes()
signal.signal(signal.SIGTERM, signal_handler)
client.run(TOKEN)