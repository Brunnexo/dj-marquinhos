import re
from typing import Optional
import discord
import strings


async def validate_interaction(interaction: discord.Interaction):
    await interaction.response.defer()
    voice = interaction.user.voice
    if voice:
        return True
    else:
        await interaction.followup.send(strings.ERR_N_CON)
        return False
    

async def validate_message(message: discord.Message):
    voice = message.author.voice
    if voice:
        return True
    else:
        await message.reply(strings.ERR_N_CON)
        return False

def extract_mp3_url(txt: str) -> Optional[str]:
    regex = r"https?://[^\s\"']+\.mp3(?:\?[^\s\"']*)?"
    urls = re.findall(regex, txt)
    
    if (len(urls) > 0):
        return urls[0]
    
    return None

def embed_message(*, description: str = None,  name: str  = None, value: str  = None) -> discord.Embed:
    embed = discord.Embed(description=description, color=0xe69138)
    embed.add_field(name=name, value=value)
    return embed