from pytubefix import YouTube, exceptions
from sound_platform import SoundPlatform, SoundPlatformException

import requests
import logging
import re
import time

from functools import lru_cache

logger = logging.getLogger(__name__)
logging.basicConfig(filename='dj-marquinhos.log', level=logging.INFO)

CACHE_SIZE = 1024

class YouTubePlatform(SoundPlatform):
    def __init__(self, url: str):
        self.__url = url
        self.__title = None
    
    def title(self) -> str:
        if self.__title is None:
            yt: YouTube = YouTubePlatform.get_youtube_obj(self.__url)
            self.__title = yt.title
        
        return self.__title
    
    def raw_url(self) -> str:
        return self.__url
    
    def platform(self): return "YouTube"

    @staticmethod
    @lru_cache(maxsize=CACHE_SIZE)
    def get_youtube_obj(url: str) -> YouTube:
        return YouTube(url, use_oauth=True, allow_oauth_cache=True)
    
    @staticmethod
    @lru_cache(maxsize=CACHE_SIZE)
    def get_stream_url(url):
        audio = None
        try:
            video = YouTubePlatform.get_youtube_obj(url)
            streams = video.streams
            audio = streams.get_audio_only()
        except exceptions.AgeRestrictedError as e:
            raise SoundPlatformException("🔞 **Este link é restrito por idade!**")
        
        if audio is None: raise SoundPlatformException("Não há stream disponível para a URL inserida")
        return audio.url
    
    def url(self) -> str:
        t1 = round(time.time() * 1000)
        logger.info(f"Obtendo URL de stream do YouTube: {self.raw_url}")
        url = YouTubePlatform.get_stream_url(self.__url)
        t2 = round(time.time() * 1000)
        logger.info(f"Tempo de execução: {t2 - t1}ms :: URL de stream: {url}")
        return url
    
    def valid_url(url: str) -> bool:
        regex = re.compile(r'^(https?://)?(www\.)?(youtube|youtu|youtube-nocookie)\.(com|be)/(watch\?v=[A-Za-z0-9_-]+|embed/[A-Za-z0-9_-]+|shorts/[A-Za-z0-9_-]+|.+)$')
        return bool(regex.match(url))