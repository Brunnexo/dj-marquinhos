from pytubefix import YouTube as YT

import logging
import re

logger = logging.getLogger("youtube_client")
logging.basicConfig(filename='bot.log', level=logging.INFO)

import requests

def valid_url(url: str) -> bool:
    return True if re.search("^(?:https?:\/\/)?(?:(?:www\.)?youtube.com\/watch\?v=|youtu.be\/)(\w+)", url) else False
    
class YouTube:
    def __init__(self, url: str):
        self._url = url
        self._title = None
    
    def title(self) -> str:
        if self._title is not None: return self._title
        
        r = requests.get(self._url, )
        html = r.text
        
        self._title = html[html.index("<title>") + 7:(html.index("</title>") - len(" - YouTube"))]
        
        return self._title
    
    def youtube_url(self) -> str:
        return self._url
    
    def url(self) -> str:
        video: YT = YT(self._url, use_oauth=True, allow_oauth_cache=True)
        streams = video.streams
        audio = None
        
        for itag in [141, 140, 139, 251, 250, 249, 171]:
            if audio is not None: break
            else: audio = streams.get_by_itag(itag)
                
                
        if audio is None: raise Exception("Não há stream disponível para a URL inserida")
        
        self._title = str(video.title)
        
        return audio.url