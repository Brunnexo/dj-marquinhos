import time

from typing import Dict, List, Optional

from youtube_client import YouTube
from discord import Client, FFmpegPCMAudio, VoiceChannel, VoiceClient, Guild, Interaction

import utils

_connections: Dict[int, VoiceClient] = {}
_playlist: Dict[int, List[YouTube]] = {}

FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn -filter:a "volume=0.25"'}

class DiscordControl:
    
    def __init__(self, client: Client):
        self._client = client
    
    async def play(self, guild: Guild, channel: VoiceChannel, url: str) -> Optional[str]:
        if guild.id not in _connections: await self.join(guild, channel)
            
        client = _connections[guild.id]
        
        if not client.is_connected():
            await self.join(guild, channel)
            client = _connections[guild.id]
        
        if not client.is_playing():
            yt = YouTube(url)
            source = FFmpegPCMAudio(yt.url(), **FFMPEG_OPTIONS)
            source.read()
            client.play(source, after = lambda e: self.play_next(guild, e))
            return yt.title()
        else:
            self.queue(guild, url)
    
    def play_pause(self, guild: Guild) -> bool:
        if guild.id not in _connections: return False
        
        client = _connections[guild.id]
        
        if client.is_playing():
            client.pause()
            return False
        else:
            client.resume()
            return True

    
    def pause(self, guild: Guild):
        if guild.id not in _connections: return
        
        client = _connections[guild.id]
        
        if client: client.pause()
        
    def resume(self, guild: Guild):
        if guild.id not in _connections: return
        
        client = _connections[guild.id]
        
        if client: client.resume()
    
    def stop(self, guild: Guild):
        if guild.id not in _connections: return
        
        client = _connections[guild.id]
        
        if client: client.stop()
     
    def skip(self, guild: Guild) -> Optional[List[str]]:
        if guild.id not in _connections: return
        
        client = _connections[guild.id]
        
        if client: client.stop()
        
        return self.play_next(guild, None)
    
    def will_queue(self, guild: Guild) -> bool:
        return guild.id in _connections or guild.id in _playlist
    
    def play_next(self, guild: Guild, e: Exception) -> Optional[List[str]]:
        if e: raise e
        
        if guild.id not in _playlist: return
        
        queue = _playlist[guild.id]
        
        if not queue: queue = []
        
        client = _connections[guild.id]
        
        if not client or not client.is_connected(): queue.clear()
        
        if len(queue) > 0:
            yt = queue.pop(0)
            source = FFmpegPCMAudio(yt.url(), **FFMPEG_OPTIONS)
            time.sleep(1.5)
            client.play(source, after = lambda e: self.play_next(guild, e))
            return [yt.youtube_url(), yt.title()]
    
    async def show_queue(self, interaction: Interaction):
        guild_id = interaction.guild.id
        
        if guild_id in _playlist:
            queue = _playlist[guild_id]
            
            if queue:
                msg = ""
                for i in range(len(queue)): 
                    msg += f"{i + 1}. **{queue[i].title()}**"
                    if (i < len(queue) - 1): msg += "\n"
                
                await interaction.followup.send(embed=utils.embed_message(description="🎵 Fila de reprodução", name="Lista", value=msg))
                return
        
        await interaction.followup.send("A lista está **vazia**!")
    
    def clear_queue(self, guild: Guild):
        if guild.id in _playlist:
            queue = _playlist[guild.id]
            if queue: _playlist[guild.id] = []
                
    def queue(self, guild: Guild, url: str):
        queue = []
        
        if guild.id in _playlist: queue = _playlist[guild.id]
        
        queue.append(YouTube(url))
        _playlist[guild.id] = queue
    
    def connections_count(selff):
        return len(_connections)
    
    async def join(self, guild: Guild, channel: VoiceChannel):
        voice_client: VoiceClient = await channel.connect()
        
        if voice_client: _connections[guild.id] = voice_client
        
    async def leave(self, guild: Guild):
        if guild.id in _connections:
            client = _connections.pop(guild.id)
            await client.disconnect()