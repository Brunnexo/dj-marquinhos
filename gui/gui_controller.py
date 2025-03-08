from abc import ABC, abstractmethod

class GUIController(ABC):
    
    @abstractmethod
    def init(self): pass
    
    @abstractmethod
    def tick(self): pass
    
    @abstractmethod
    def splash(self): pass