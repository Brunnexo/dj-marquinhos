import sys
import io

import discord

args = sys.argv

def is_raspberrypi():
    try:
        with io.open('/sys/firmware/devicetree/base/model', 'r') as m:
            if 'raspberry pi' in m.read().lower(): return True
    except Exception: pass
    return False

async def validate_interaction(interaction: discord.Interaction):
    await interaction.response.defer()
    voice = interaction.user.voice
    if voice:
        return True
    else:
        await interaction.followup.send("🚫 Você não está conectado a nenhum canal de voz!")
        return False
    
async def validate_message(message: discord.Message):
    voice = message.author.voice
    if voice:
        return True
    else:
        await message.reply("🚫 Você não está conectado a nenhum canal de voz!")
        return False

def gui_arg():
    if "--gui" in args:
        index = args.index("--gui")
        if (len(args) > index): return args[index + 1].lower()

def token_arg():
    if "--token" in args:
        index = args.index("--token")
        if (len(args) > index): return args[index + 1]
        
    return None

def embed_message(*, description: str = None,  name: str  = None, value: str  = None) -> discord.Embed:
    embed = discord.Embed(description=description, color=0xe69138)
    embed.add_field(name=name, value=value)
    return embed