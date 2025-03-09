import os
import logging

from typing import Optional
import psutil

from abc import ABC, abstractmethod

# Logger
logger = logging.getLogger(__name__)
logging.basicConfig(filename='dj-marquinhos.log', level=logging.DEBUG)

CONTROLLER = os.getenv("DJ_DISCORD_GUI_CONTROLLER")

class GUIUpdate:
    cpu_usage: float
    ram_usage: float
    user: str
    command: str
    channels_count: int

class GUIController(ABC):
    @abstractmethod
    def init(self): pass
    
    @abstractmethod
    def tick(self, update: GUIUpdate): pass
    
    @abstractmethod
    def clear(self): pass
    
    @abstractmethod
    def splash(self): pass
    
    @abstractmethod
    def interval(self) -> int: pass
    
    def name() -> Optional[str]: pass
        
class GUIHandler:
    def __init__(self):
        self.__last_command = ""
        self.__last_user = ""
        self.__channels_count = 0
        
        self.__controller = None
        
        logger.debug("Controladores GUI dispon\u00EDveis:")
        for controller in GUIController.__subclasses__():
            name = controller.name()
            logger.debug(name)
            if CONTROLLER == name:
                self.__controller = controller()
                logger.info(f"Controlador GUI definido: {self.__controller.name()}")
            
        if self.__controller is None:
            logger.warning("Nenhum controlador GUI definido")
    
    def set_command(self, command: str):
        if self.__controller is None: return
        self.__last_command = command
        
    def set_user(self, user: str):
        if self.__controller is None: return
        self.__last_user = user
        
    def set_channels_count(self, count: int):
        if self.__controller is None: return
        self.__channels_count = count
        
    def init(self):
        if self.__controller is None: return
        self.__controller.init()
        
    def tick(self):
        if self.__controller is None: return
        update = GUIUpdate()
        
        update.channels_count = self.__channels_count
        update.user = self.__last_user
        update.command = self.__last_command
        update.cpu_usage = psutil.cpu_percent()
        update.ram_usage = psutil.virtual_memory()[2]
        
        self.__controller.tick(update=update)
    
    def interval(self) -> int:
        if self.__controller is None: return 0
        return self.__controller.interval()
    
    def clear(self):
        if self.__controller is None: return
        self.__controller.clear()
        
    def splash(self):
        if self.__controller is None: return
        self.__controller.splash()