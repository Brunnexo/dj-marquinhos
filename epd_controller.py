import time
import platform
import sys

from PIL import Image, ImageDraw, ImageFont

sys.path.append("./waveshare_epd")

from gui_controller import GUIController, GUIUpdate

# Este módulo só funciona no Raspberry Pi
if platform.system() == "Linux": from waveshare_epd import epd2in13_V4

font = ImageFont.truetype("./font/Font.ttc", 12)
font_lg = ImageFont.truetype("./font/Font.ttc", 16)
splash = Image.open("./images/epd-splash.bmp")
logo = Image.open("./images/dj.bmp")

class EPDController(GUIController):
    def __init__(self):
        self.__epd = epd2in13_V4.EPD()
        
        self.__ticked = False
        self.__display_init = False

        self.__user = ""
        self.__command = ""
        self.__channels = 0
        self.__cpu_usage_value = 0
        self.__ram_usage_value = 0

        self.__WIDTH = self.__epd.width
        self.__HEIGHT = self.__epd.height

    def init(self):
        if not self.__display_init:
            self.__epd.init()
            self.clear()
            self.__display_init = True
            
    def tick(self, update: GUIUpdate):
        self.init()
        
        self.__channels = update.channels_count
        self.__command = update.command
        self.__cpu_usage_value = update.cpu_usage
        self.__ram_usage_value = update.ram_usage
        self.__channels = update.channels_count
        
        frame = self.__blank()
        
        self.__cpu_usage(frame)
        self.__ram_usage(frame)
        self.__dj_logo(frame)
        self.__show_command(frame)
        self.__show_channels_count(frame)
        
        if self.__ticked:
            self.__epd.displayPartial(self.__epd.getbuffer(frame))
        else:
            self.__epd.display(self.__epd.getbuffer(frame))
            self.__ticked = True

    def clear(self):
        frame = self.__blank()
        self.__epd.display(self.__epd.getbuffer(frame))

    def splash(self):
        self.init()
        self.__epd.display(self.__epd.getbuffer(splash))
        time.sleep(1)
        self.__epd.Clear(0xFF)

    def interval(self) -> int:
        return 5
        
    @staticmethod
    def name() -> str:
        return "EPD_CONTROLLER"

    def __blank(self):
        return Image.new('1', (self.__HEIGHT, self.__WIDTH), 255)

    def __dj_logo(self, frame):
        self.init()
        frame.paste(logo, (self.__HEIGHT - 71, self.__WIDTH - 71))

    def __cpu_usage(self, frame):
        self.init()
        draw = ImageDraw.Draw(frame)
        x, y = 0, 5
        xy = (x, y)
        
        cpu = int(self.__cpu_usage_value / 100 * self.__HEIGHT)
        
        draw.rectangle([ xy, (self.__HEIGHT, y + 15)], fill=1)
        draw.text((x, y + 5), f"Uso de CPU: {self.__cpu_usage_value}%", font = font, fill = 0)
        draw.rectangle([ xy, (cpu, y + 5)], fill=0)
    
    def __ram_usage(self, frame):
        self.init()
        draw = ImageDraw.Draw(frame)
        x, y = 0, 25
        xy = (x, y)
        
        ram = int(self.__ram_usage_value / 100 * self.__HEIGHT)
        
        draw.rectangle([ xy, (self.__HEIGHT, y + 15)], fill=1)
        draw.text((x, y + 5), f"Uso de RAM: {self.__ram_usage_value}%", font = font, fill = 0)
        draw.rectangle([ xy, (ram, y + 5)], fill=0)

    def __show_command(self, frame):
        self.init()
        
        draw = ImageDraw.Draw(frame)
        
        x, y = 0, 45
        
        if len(self.__command) > 0 and len(self.__user) > 0:
            draw.text((x, y), f"[{self.__user}] usou", font = font, fill = 0)
            draw.text((x, y + 16), f"/{self.__command}", font = font_lg, fill = 0)
    
    def __show_channels_count(self, frame):
        self.init()
        draw = ImageDraw.Draw(frame)
        x, y = 0, 110
        
        if self.__channels > 0: draw.text((x, y), f"Canais de voz ativos: {self.__channels}", font = font, fill = 0)