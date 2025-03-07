from abc import ABC, abstractmethod
import strings
import logging

# Logger
logger = logging.getLogger(__name__)
logging.basicConfig(filename='dj-marquinhos.log', level=logging.INFO)

class SoundPlatformException(Exception): ...

class SoundPlatform(ABC):

    def __init__(self, url: str):
        self._url = url

    @abstractmethod
    def url(self) -> str:
        pass
    
    @abstractmethod
    def title(self) -> str:
        pass
    
    @abstractmethod
    def raw_url(self) -> str:
        pass
    
    @abstractmethod
    def platform(self) -> str:
        pass
    
    @staticmethod
    def valid_url(url: str) -> bool:
        pass
    

class PlatformHandler:
    def __init__(self, url: str):
        self._url = url
    
    def url(self) -> str:
        for platform in SoundPlatform.__subclasses__():
            if platform.valid_url(self._url):
                return platform(self._url).url()
        
        raise SoundPlatformException(strings.ERR_EXCEPTION_INVALID_URL)

    def title(self) -> str:
        for platform in SoundPlatform.__subclasses__():
            if platform.valid_url(self._url):
                def_platform = platform(self._url)
                return f"{def_platform.title()} - {def_platform.platform()}"

    def platform(self) -> str:
        for platform in SoundPlatform.__subclasses__():
            if platform.valid_url(self._url):
                return platform(self._url).platform()
    
    def raw_url(self) -> str:
        for platform in SoundPlatform.__subclasses__():
            if platform.valid_url(self._url):
                return platform(self._url).raw_url()
    
    @staticmethod
    def valid_url(url: str) -> bool:
        for platform in SoundPlatform.__subclasses__():
            if platform.valid_url(url): return True
            
        return False
    
    @staticmethod
    def show_classes():
        for platform in SoundPlatform.__subclasses__():
            logger.info(f"{platform.__name__} > SoundPlatform")