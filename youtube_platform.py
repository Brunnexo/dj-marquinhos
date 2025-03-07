from pytubefix import YouTube, exceptions
from sound_platform import SoundPlatform, SoundPlatformException

import strings
import logging
import re

import requests

logger = logging.getLogger(__name__)
logging.basicConfig(filename='dj-marquinhos.log', level=logging.INFO)


class YouTubePlatform(SoundPlatform):
    def __init__(self, url: str):
        self._url = url
        self._title = None
    
    def title(self) -> str:
        if self._title is not None: return self._title
        
        r = requests.get(self._url)
        html = r.text
        
        self._title = html[html.index("<title>") + 7:(html.index("</title>") - len(" - YouTube"))]
        
        return self._title
    
    def raw_url(self) -> str:
        return self._url
    
    def platform(self): return "YouTube"
    
    def url(self) -> str:
        audio = None
        
        try:
            video: YouTube = YouTube(self._url, use_oauth=True, allow_oauth_cache=True)
            streams = video.streams
            
            for itag in [141, 140, 139, 251, 250, 249, 171]:
                if audio is not None: break
                else: audio = streams.get_by_itag(itag)
            
            self._title = str(video.title)
        except exceptions.AgeRestrictedError as e:
            raise SoundPlatformException(strings.ERR_EXCEPTION_AGE)
        
        if audio is None: raise SoundPlatformException(strings.ERR_EXCEPTION_STREAM)
        
        return audio.url
    
    def valid_url(url: str) -> bool:
        regex = re.compile(r'^(https?://)?(www\.)?(youtube|youtu|youtube-nocookie)\.(com|be)/(watch\?v=[A-Za-z0-9_-]+|embed/[A-Za-z0-9_-]+|shorts/[A-Za-z0-9_-]+|.+)$')
        return bool(regex.match(url))