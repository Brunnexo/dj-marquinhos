import re
from typing import Optional

from sound_platform import SoundPlatform
from urllib.parse import urljoin, urlparse

class MP3Platform(SoundPlatform):
    def __init__(self, url: str):
        self._url = url
        self._title = urljoin(url, urlparse(url).path).split("/")[-1]
    
    @staticmethod
    def extract_mp3_url(txt: str) -> Optional[str]:
        regex = r"https?://[^\s\"']+\.mp3(?:\?[^\s\"']*)?"
        urls = re.findall(regex, txt)
    
        if (len(urls) > 0):
            return urls[0]
    
        return None
        
    def title(self):
        return self._title
    
    def raw_url(self) -> str:
        return self._url
    
    def platform(self) -> str:
        return "MP3"
    
    def url(self) -> str:
        return self._url
    
    def valid_url(url: str) -> bool:
        return urljoin(url, urlparse(url).path).endswith(".mp3")