import time
import sys
import os
import psutil

epd_dir = "./waveshare_epd"

if os.path.exists(epd_dir):
    sys.path.append(epd_dir)
else: raise ModuleNotFoundError("waveshare_epd")
    
from waveshare_epd import epd2in13_V4
from PIL import Image, ImageDraw, ImageFont

font = ImageFont.truetype("./font/Font.ttc", 12)
font_lg = ImageFont.truetype("./font/Font.ttc", 16)

splash = Image.open("./images/splash.bmp")

class EPD:
    def __init__(self):
        self._epd = epd2in13_V4.EPD()
        self._plotted = False
        self._display_init = False
        
        self.WIDTH = self._epd.width
        self.HEIGHT = self._epd.height
        
        self._user = ""
        self._command = ""
        self._channels = 0
        
        
    def _init(self):
        if not self._display_init:
            self._epd.init()
            self.clear()
            self._display_init = True
    
    def clear(self):
        self._epd.Clear(0xFF)
        frame = self._blank()
        self._epd.display(self._epd.getbuffer(frame))
        
    def command(self, user: str, command: str):
        self._init()
        self._user = user
        self._command = command
        
    def channels(self, channels: int):
        self._channels = channels    

    def _blank(self):
        return Image.new('1', (self.HEIGHT, self.WIDTH), 255)

    def _dj_logo(self, frame):
        self._init()
        logo = Image.open("./images/dj.bmp")
        frame.paste(logo, (self.HEIGHT - 71, self.WIDTH - 71))

    def _cpu_usage(self, frame):
        self._init()
        draw = ImageDraw.Draw(frame)
        x, y = 0, 5
        xy = (x, y)
        usage = psutil.cpu_percent()
        cpu = int(usage / 100 * self.HEIGHT)
        draw.rectangle([ xy, (self.HEIGHT, y + 15)], fill=1)
        draw.text((x, y + 5), f"Uso de CPU: {usage}%", font = font, fill = 0)
        draw.rectangle([ xy, (cpu, y + 5)], fill=0)
    
    def _ram_usage(self, frame):
        self._init()
        draw = ImageDraw.Draw(frame)
        x, y = 0, 25
        xy = (x, y)
        usage = psutil.virtual_memory()[2]
        ram = int(usage / 100 * self.HEIGHT)
        draw.rectangle([ xy, (self.HEIGHT, y + 15)], fill=1)
        draw.text((x, y + 5), f"Uso de RAM: {usage}%", font = font, fill = 0)
        draw.rectangle([ xy, (ram, y + 5)], fill=0)

    def _show_command(self, frame):
        self._init()
        
        draw = ImageDraw.Draw(frame)
        
        x, y = 0, 45
        
        if len(self._command) > 0 and len(self._user) > 0:
            draw.text((x, y), f"[{self._user}] usou", font = font, fill = 0)
            draw.text((x, y + 16), f"/{self._command}", font = font_lg, fill = 0)
    
    def _show_channels_count(self, frame):
        self._init()
        draw = ImageDraw.Draw(frame)
        x, y = 0, 110
        
        if self._channels > 0: draw.text((x, y), f"Canais de voz ativos: {self._channels}", font = font, fill = 0)
    
    def splash(self):
        self._init()
        self._epd.display(self._epd.getbuffer(splash))
        time.sleep(1)        
        self._epd.Clear(0xFF)
    
    def plot(self):
        self._init()
        
        frame = self._blank()
        
        self._cpu_usage(frame)
        self._ram_usage(frame)
        self._dj_logo(frame)
        self._show_command(frame)
        self._show_channels_count(frame)
        
        if self._plotted:
            self._epd.displayPartial(self._epd.getbuffer(frame))
        else:
            self._epd.display(self._epd.getbuffer(frame))
            self._plotted = True