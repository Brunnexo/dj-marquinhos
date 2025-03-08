import os
from typing import Optional
import psutil

from abc import ABC, abstractmethod

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
        
        for controller in GUIController.__subclasses__():
            if CONTROLLER == controller.name(): self.__controller = controller()
        
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