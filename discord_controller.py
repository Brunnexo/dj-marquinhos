# Python
import time
from typing import Dict, List, Optional

# Discord.py
from discord import FFmpegPCMAudio, VoiceChannel, VoiceClient, Guild, Interaction

import utils

from sound_platform import PlatformHandler

FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn -filter:a "volume=0.25"'}

class DiscordController:
    
    def __init__(self):
        self.__connections: Dict[int, VoiceClient] = {}
        self.__keep_list: List[int] = []
        self.__playlist: Dict[int, List[PlatformHandler]] = {}
    
    async def play(self, guild: Guild, channel: VoiceChannel, url: str) -> Optional[str]:
        if guild.id not in self.__connections: await self.join(guild, channel)
        
        client = self.__connections[guild.id]
        
        if not client.is_connected():
            await self.join(guild, channel)
            client = self.__connections[guild.id]
        
        if not client.is_playing():
            platform = PlatformHandler(url)
            return self.__platform_play(platform, client, guild)

        else: self.queue(guild, url)
    
    def __platform_play(self, platform: PlatformHandler, client: VoiceClient, guild: Guild) -> str:
        source = FFmpegPCMAudio(platform.url(), **FFMPEG_OPTIONS)
        source.read()
        client.play(source, after = lambda e: self.play_next(guild, e))
        return platform.title()
    
    def play_pause(self, guild: Guild) -> bool:
        if guild.id not in self.__connections: return False
        
        client = self.__connections[guild.id]
        
        if client.is_playing():
            client.pause()
            return False
        else:
            client.resume()
            return True

    
    def pause(self, guild: Guild):
        if guild.id not in self.__connections: return
        
        client = self.__connections[guild.id]
        
        if client: client.pause()
        
    def resume(self, guild: Guild):
        if guild.id not in self.__connections: return
        
        client = self.__connections[guild.id]
        
        if client: client.resume()
    
    def stop(self, guild: Guild):
        if guild.id not in self.__connections: return
        
        client = self.__connections[guild.id]
        
        if client: client.stop()

    def skip(self, guild: Guild) -> Optional[List[str]]:
        if guild.id not in self.__connections: return
        
        client = self.__connections[guild.id]
        
        if client: client.stop()
        
        return self.play_next(guild, None)
    
    def will_queue(self, guild: Guild) -> bool:
        return guild.id in self.__connections or guild.id in self.__playlist
    
    def play_next(self, guild: Guild, e: Exception) -> Optional[List[str]]:
        if e: raise e
        
        if guild.id not in self.__playlist: return
        
        queue = self.__playlist[guild.id]
        
        if not queue: queue = []
        
        client = self.__connections[guild.id]
        
        if not client or not client.is_connected(): queue.clear()
        
        if len(queue) > 0:
            platform = queue.pop(0)
            self.__platform_play(platform, client, guild)
            return [platform.raw_url(), platform.title()]
    
    async def show_queue(self, interaction: Interaction):
        guild_id = interaction.guild.id
        
        if guild_id in self.__playlist:
            queue = self.__playlist[guild_id]
            
            if queue:
                msg = ""
                for i in range(len(queue)): 
                    msg += f"{i + 1}. **{queue[i].title()}**"
                    if (i < len(queue) - 1): msg += "\n"
                
                await interaction.followup.send(embed=utils.embed_message(description="🎵 Fila de reprodução", name="Lista", value=msg))
                return
        
        await interaction.followup.send("A fila está **vazia**!")
    
    def keep(self, guild: Guild):
        self.__keep_list.append(guild.id)
    
    async def clean(self):
        timestamp = round(time.time())
        
        deletions = []

        for id in self.__connections:
            if id in self.__keep_list: continue
            
            client = self.__connections[id]
            
            if not client.is_connected():
                await self.__disconnect_client(client, id, deletions=deletions)
                continue
            
            if not client.is_playing() and not client.is_paused():
                delta = round((timestamp - client.timestamp) / 1000)
                if delta > 60: await self.__disconnect_client(client, id, deletions=deletions)

        for id in deletions:
            self.__connections[id].cleanup()
            del self.__connections[id]
    
    async def __disconnect_client(self, client: VoiceClient, id: int, *, deletions: List[int] = None):
        await client.disconnect()
        if deletions is not None: deletions.append(id)
    
    def clear_queue(self, guild: Guild):
        if guild.id in self.__playlist:
            queue = self.__playlist[guild.id]
            if queue: self.__playlist[guild.id] = []
                
    def queue(self, guild: Guild, url: str):
        queue = []
        
        if guild.id in self.__playlist: queue = self.__playlist[guild.id]
        
        queue.append(PlatformHandler(url))
        self.__playlist[guild.id] = queue
    
    def connections_count(self):
        return len(self.__connections)
    
    async def join(self, guild: Guild, channel: VoiceChannel):
        voice_client: VoiceClient = await channel.connect()
        voice_client.timestamp = round(time.time())
        
        if voice_client: self.__connections[guild.id] = voice_client
        
    async def leave(self, guild: Guild):
        deletions = []
        if guild.id in self.__connections:
            client = self.__connections[guild.id]
            await self.__disconnect_client(client, guild.id, deletions=deletions)
            
        for id in deletions:
            self.__connections[id].cleanup()
            del self.__connections[id]