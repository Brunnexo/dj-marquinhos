NAME = "TKINTER"

import os
import sys
import tkinter as tk
from tkinter import ttk

from PIL import Image, ImageTk

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from gui_controller import GUIController, GUIUpdate

dj_image = Image.open("./gui/images/dj-large.png").resize((100, 100))
balloon = Image.open("./gui/images/balloon.png").resize((297, 84))


class TKInterController(GUIController):
    def __init__(self):
        self.__win = tk.Tk()
        
        self.__user = ""
        self.__command = ""
        self.__cpu_usage_value = tk.IntVar()
        self.__ram_usage_value = tk.IntVar()
        
        self.__WIDTH = 480
        self.__HEIGHT = 320
        
        self.__label_cpu = tk.Label(text="Uso de CPU")
        self.__pb_cpu = ttk.Progressbar(variable=self.__cpu_usage_value)
        
        self.__label_ram = tk.Label(text="Uso de RAM")
        self.__pb_ram = ttk.Progressbar(variable=self.__ram_usage_value)
        
        self.__label_command = tk.Label(text="", width=40, bg="white")
        
        self.__label_count = tk.Label(text="", width=40)

        self.__balloon_photo = ImageTk.PhotoImage(balloon)
        self.__balloon = tk.Label(image=self.__balloon_photo)
        self.__balloon.image = self.__balloon_photo
        
        self.__logo_photo = ImageTk.PhotoImage(dj_image)
        self.__logo = tk.Label(image=self.__logo_photo)
        self.__logo.image = self.__logo_photo
    
    def init(self):
        self.__win.title("DJ Marquinhos")
        self.__win.geometry(f"{self.__WIDTH}x{self.__HEIGHT}")
        self.__win.resizable(False, False)

        
        
        self.__label_count.place(x=10, y=10,  width=self.__WIDTH, height=30)
        
        self.__label_cpu.place(x=10, y=(self.__HEIGHT - 100),  width=((self.__WIDTH - 20) - 120), height=20)
        self.__pb_cpu.place(x=10, y=(self.__HEIGHT - 80), width=((self.__WIDTH - 20) - 120), height=20)
        
        self.__label_ram.place(x=10, y=(self.__HEIGHT - 60), width=((self.__WIDTH - 20) - 120), height=20)
        self.__pb_ram.place(x=10, y=(self.__HEIGHT - 40), width=((self.__WIDTH - 20) - 120), height=20)
        
        self.__logo.place(x=(self.__WIDTH - self.__logo_photo.width()), y=(self.__HEIGHT - self.__logo_photo.height()), width=self.__logo_photo.width(), height=self.__logo_photo.height())
        self.__logo.lower()
        

        
    def tick(self, update: GUIUpdate):
        cpu = update.cpu_usage
        ram = update.ram_usage
        count = update.channels_count
        
        self.__label_count.config(text=f"O DJ está presente em {count} cana{'is' if count > 1 else 'l'}", font=(None, 14, "bold"))
        
        self.__label_cpu.config(text=f"Uso de CPU: {cpu}%")
        self.__cpu_usage_value.set(cpu)
        
        self.__label_ram.config(text=f"Uso de RAM: {ram}%")
        self.__ram_usage_value.set(ram)
        
        self.__command = update.command
        self.__user = update.user
        
        if len(self.__command) > 0 and len(self.__user) > 0:
            self.__balloon.place(x=(self.__WIDTH - self.__balloon_photo.width() - 40), y=(self.__HEIGHT - self.__balloon_photo.height() - 120), width=self.__balloon_photo.width(), height=self.__balloon_photo.height())
            self.__balloon.lower()
            self.__label_command.place(x=(self.__WIDTH - 320), y=(self.__HEIGHT - 188), width=260, height=28)
            self.__label_command.config(text=f"{self.__user} usou /{self.__command}", font=(None, 12, "bold"), justify="left")
        
        self.__win.update()
    
    def clear(self):
        self.__win.destroy()

    def splash(self): pass
    
    def interval(self): return 0
    
    @staticmethod
    def name() -> str:
        return NAME