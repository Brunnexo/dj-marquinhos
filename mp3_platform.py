from sound_platform import SoundPlatform

from urllib.parse import urljoin, urlparse

import strings

class MP3Platform(SoundPlatform):
    def __init__(self, url: str):
        self._url = url
        self._title = urljoin(url, urlparse(url).path).split("/")[-1]
        
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