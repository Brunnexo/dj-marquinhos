from pytubefix import YouTube, exceptions
from sound_platform import SoundPlatform, SoundPlatformException

import requests
import logging
import re
import time

from functools import lru_cache

logger = logging.getLogger(__name__)
logging.basicConfig(filename='dj-marquinhos.log', level=logging.INFO)

@lru_cache(maxsize=1024)
def get_stream_url(url: str):
    logger.debug(f"Obtendo URL de stream do YouTube: {url}")
    
    audio = None
    
    t1 = round(time.time() * 1000)
    
    try:
        video: YouTube = YouTube(url, use_oauth=True, allow_oauth_cache=True)
        streams = video.streams
        
        logger.debug("Buscando melhor ITAG...")
        audio = streams.get_audio_only()
    except exceptions.AgeRestrictedError as e:
        raise SoundPlatformException("🔞 **Este link é restrito por idade!**")
    
    if audio is None: raise SoundPlatformException("Não há stream disponível para a URL inserida")
    
    t2 = round(time.time() * 1000)
    
    logger.debug(f"ITAG encontrado: {audio.itag}. Tempo de execução: {t2 - t1}ms")
    logger.debug(f"URL de stream: {audio.url}")
    
    return audio.url, str(video.title)

class YouTubePlatform(SoundPlatform):
    def __init__(self, url: str):
        self.__url = url
        self.__title = None
    
    def title(self) -> str:
        if self.__title is not None and not bool(self.__title.strip()):
            logger.debug(f"Título no YouTube: {self.__title} de {self.__url}")
            return self.__title
        
        r = requests.get(self.__url)
        html = r.text
        
        self.__title = html[html.index("<title>") + 7:(html.index("</title>") - len(" - YouTube"))]
        
        logger.debug(f"Título no YouTube: {self.__title} de {self.__url}")
        return self.__title
    
    def raw_url(self) -> str:
        return self.__url
    
    def platform(self): return "YouTube"
    
    def url(self) -> str:
        url, self.__title = get_stream_url(self.__url)
        return url
    
    def valid_url(url: str) -> bool:
        regex = re.compile(r'^(https?://)?(www\.)?(youtube|youtu|youtube-nocookie)\.(com|be)/(watch\?v=[A-Za-z0-9_-]+|embed/[A-Za-z0-9_-]+|shorts/[A-Za-z0-9_-]+|.+)$')
        return bool(regex.match(url))