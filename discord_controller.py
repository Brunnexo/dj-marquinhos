# Python
import time
import logging
from typing import Dict, List, Optional, Union

# Discord.py
from discord import FFmpegPCMAudio, VoiceChannel, VoiceClient, Guild, Interaction, TextChannel

InteractionChannel = Union[VoiceChannel, TextChannel]

import utils

from sound_platform import PlatformHandler, SoundPlatformException

FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn -filter:a "volume=0.25"'}

logger = logging.getLogger(__name__)
logging.basicConfig(filename='dj-marquinhos.log', level=logging.INFO)


class DiscordConnection:
    def __init__(self, client: VoiceClient, channel: VoiceChannel, interaction_channel: InteractionChannel):
        self.__keep = False
        self.__client: VoiceClient = client
        self.__channel: VoiceChannel = channel
        self.__interaction_channel: InteractionChannel = interaction_channel
        self.__timestamp: float = time.time()
    
    def __get_keep(self) -> bool:
        keep = self.__keep
        if keep: self.__timestamp = time.time()
        return keep
    
    def __set_keep(self, keep: bool):
        self.__keep = keep
        
    def __del_keep(self):
        del self.__keep
    
    def __get_client(self) -> VoiceClient:
        client = self.__client
        if client.is_playing(): self.__timestamp = time.time()
        return client
    
    def __set_client(self, client: VoiceClient):
        self.__client = client
    
    def __del_client(self):
        del self.__client
    
    def __get_channel(self) -> VoiceChannel:
        return self.__channel
    
    def __set_channel(self, channel: VoiceChannel):
        self.__channel = channel
        
    def __del_channel(self):
        del self.__channel
        
    def __get_timestamp(self) -> float:
        return self.__timestamp
    
    def __set_timestamp(self, timestamp: float):
        self.__timestamp = timestamp

    def __del_timestamp(self):
        del self.__timestamp

    def __get_interaction_channel(self) -> InteractionChannel:
        return self.__interaction_channel
    
    def __set_interaction_channel(self, interaction_channel: InteractionChannel):
        self.__interaction_channel = interaction_channel

    def __del_interaction_channel(self):
        del self.__interaction_channel

    keep: bool = property(
        fget = __get_keep,
        fset = __set_keep,
        fdel = __del_keep
    )
    
    client: VoiceClient = property(
        fget = __get_client,
        fset = __set_client,
        fdel = __del_client
    )
    
    channel: VoiceChannel = property(
        fget = __get_channel,
        fset = __set_channel,
        fdel = __del_channel
    )
    
    interaction_channel: InteractionChannel = property(
        fget = __get_interaction_channel,
        fset = __set_interaction_channel,
        fdel = __del_interaction_channel
    )
    
    timestamp: float = property(
        fget = __get_timestamp,
        fset = __set_timestamp,
        fdel = __del_timestamp
    )


class DiscordController:
    
    def __init__(self):
        self.__connections: Dict[int, DiscordConnection] = {}
        self.__playlist: Dict[int, List[PlatformHandler]] = {}
        self.__deletions = set({})
    
    async def play(self, interaction: Interaction, url: str) -> Optional[str]:
        guild = interaction.guild
        channel = interaction.user.voice.channel
        
        if guild.id not in self.__connections: await self.join(interaction)
        
        user = interaction.user
        
        connection = self.__connections[guild.id]
        
        members = connection.channel.members
        user_connected = len([member for member in members if member.id == user.id]) > 1
        
        if not user_connected: 
            await connection.client.move_to(channel)
            self.__connections[guild.id].channel = channel
        
        client = connection.client
        
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
        
        connection = self.__connections[guild.id]
        client = connection.client
        
        if client.is_playing():
            client.pause()
            return False
        else:
            client.resume()
            return True

    
    def pause(self, guild: Guild):
        if guild.id not in self.__connections: return
        client = self.__connections[guild.id].client
        if client: client.pause()
        
    def resume(self, guild: Guild):
        if guild.id not in self.__connections: return
        client = self.__connections[guild.id].client
        if client: client.resume()
    
    def stop(self, guild: Guild):
        if guild.id not in self.__connections: return
        client = self.__connections[guild.id].client
        if client: client.stop()

    def skip(self, guild: Guild) -> Optional[List[str]]:
        if guild.id not in self.__connections: return
        client = self.__connections[guild.id].client
        if client: client.stop()
        
        return self.play_next(guild, None)
    
    def will_queue(self, guild: Guild) -> bool:
        return guild.id in self.__connections or guild.id in self.__playlist
    
    def play_next(self, guild: Guild, e: Exception) -> Optional[List[str]]:
        if e: raise SoundPlatformException(str(e))
        if guild.id not in self.__playlist: return
        
        queue = self.__playlist[guild.id]
        
        if not queue: queue = []
        client = self.__connections[guild.id].client
        
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
    
    def keep(self, guild: Guild) -> Optional[bool]:
        if guild.id not in self.__connections: return None
        
        connection = self.__connections[guild.id]
        connection.keep = not connection.keep
        return connection.keep

    async def clean(self):
        timestamp = round(time.time())
        
        for id in self.__deletions:
            if id in self.__connections:
                self.__connections[id].client.cleanup()
                del self.__connections[id]

        self.__deletions.clear()

        for id in self.__connections:
            connection = self.__connections[id]
            
            if connection.keep: continue
            
            channel = connection.channel
            client = connection.client
            
            if not client.is_connected():
                self.__deletions.add(id)
                continue
            
            if len(channel.members) == 1:
                await self.__disconnect_client(id, rs="falta de ouvintes")
            
            if not client.is_playing() and not client.is_paused():
                delta = round(timestamp - connection.timestamp)
                if delta > 60: await self.__disconnect_client(id)

    
    async def __disconnect_client(self, id: int, *, rs: Optional[str] = "inatividade"):
        connection = self.__connections[id]
        
        interaction_channel = connection.interaction_channel
        
        if rs is not None:
            await interaction_channel.send(f"🚬 Estou saindo por **{rs}**...")
        
        client: VoiceClient = connection.client
        
        logger.debug(f"Desconectando VoiceClient do canal {client.channel.name}...")
        
        t1 = round(time.time() * 1000)
        await client.disconnect()
        t2 = round(time.time() * 1000)
        
        logger.debug(f"Tempo de execução: {t2 - t1}ms")
        
        self.__deletions.add(id)
    
    def clear_queue(self, guild: Guild):
        if guild.id in self.__playlist:
            queue = self.__playlist[guild.id]
            if queue: self.__playlist[guild.id] = []
                
    def queue(self, guild: Guild, url: str):
        queue = []
        
        if guild.id in self.__playlist: queue = self.__playlist[guild.id]
        
        queue.append(PlatformHandler(url))
        
        self.__playlist[guild.id] = queue
    
    def connections_count(self): return len(self.__connections)
    
    async def join(self, interaction: Interaction):
        guild = interaction.guild
        channel = interaction.user.voice.channel
        interaction_channel = interaction.channel
        
        client: VoiceClient = await channel.connect()
        
        if client: self.__connections[guild.id] = DiscordConnection(client, channel, interaction_channel)

    async def leave(self, interaction: Interaction):
        guild = interaction.guild
        
        if guild.id in self.__connections:
            await self.__disconnect_client(guild.id, rs=None)