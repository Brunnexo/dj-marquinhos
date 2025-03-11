from abc import ABC, abstractmethod
import logging

# Logger
logger = logging.getLogger(__name__)
logging.basicConfig(filename='dj-marquinhos.log', level=logging.DEBUG)

class SoundPlatformException(Exception): ...

class SoundPlatform(ABC):

    def __init__(self, url: str):
        self._url = url

    @abstractmethod
    def url(self) -> str: pass
    
    @abstractmethod
    def title(self) -> str: pass
    
    @abstractmethod
    def raw_url(self) -> str: pass
    
    @abstractmethod
    def platform(self) -> str: pass
    
    @staticmethod
    def valid_url(url: str) -> bool: pass
    

class PlatformHandler:
    def __init__(self, url: str):
        self.__url = url
        self.__stream_url = ""
        
        self.__platform = None
        self.url_processed = False

        for platform in SoundPlatform.__subclasses__():
            if platform.valid_url(self.__url):
                self.__platform = platform

        if self.__platform is None: raise SoundPlatformException("URL inválida em todas as plataformas disponíveis")
        else: logger.debug(f"{self.__platform.__name__}: {self.__url}")

    def url(self) -> str:
        if not self.url_processed:
            self.__stream_url = self.__platform(self.__url).url()
            self.url_processed = True
        
        return self.__stream_url

    def title(self) -> str:
        def_platform = self.__platform(self.__url)
        return f"{def_platform.title()} - {def_platform.platform()}"

    def raw_url(self) -> str:
        return self.__platform(self.__url).raw_url()

    def platform(self) -> str:
        return self.__platform(self.__url).platform()

    @staticmethod
    def valid_url(url: str) -> bool:
        for platform in SoundPlatform.__subclasses__():
            if platform.valid_url(url): return True

        return False
    
    @staticmethod
    def show_classes():
        logger.debug("Plataformas de som disponíveis: ")
        for platform in SoundPlatform.__subclasses__():
            logger.info(f"{platform.__name__}")