import discord
from discord_control import DiscordControl
import utils

class PlayerButtons(discord.ui.View):
    def __init__(self, control: DiscordControl):
        super().__init__()
        self._control: DiscordControl = control

    @discord.ui.button(emoji='⏯️', style=discord.ButtonStyle.primary)
    async def but_play_pause(self, interaction: discord.Interaction, button: discord.ui.Button):
        if await utils.validate_interaction(interaction):
            message_id = interaction.message.id
            embed: discord.Embed = interaction.message.embeds[0]
            
            playing = self._control.play_pause(interaction.guild)
            
            embed.description = "💿 Tocando agora!" if playing else "⏸️ Pausado!"
            
            await interaction.followup.edit_message(embed=embed, message_id=message_id)
        
    
    @discord.ui.button(emoji='⏹️', style=discord.ButtonStyle.primary)
    async def but_stop(self, interaction: discord.Interaction, button: discord.ui.Button):
        if await utils.validate_interaction(interaction):
            self._control.stop(interaction.guild)
            await interaction.followup.send("⏹️ Para tudo!")
            
    @discord.ui.button(emoji='⏭️', style=discord.ButtonStyle.primary)
    async def but_next(self, interaction: discord.Interaction, button: discord.ui.Button):
        if await utils.validate_interaction(interaction):
            skip_ret = self._control.skip(interaction.guild)
            embed: discord.Embed = interaction.message.embeds[0]
            message_id = interaction.message.id
            
            if skip_ret and len(skip_ret) > 0: embed.set_field_at(0, name=skip_ret[1], value=skip_ret[0])
            
            await interaction.followup.edit_message(embed=embed, message_id=message_id)
        