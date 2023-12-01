# legacy tkinter
import tkinter as tk
from tkinter import ttk, filedialog

# custom tkinter
import customtkinter

import os
import sounddevice
from device_controller import DeviceController

customtkinter.set_appearance_mode("System")  # Modes: "System" (standard), "Dark", "Light"
customtkinter.set_default_color_theme("blue")  # Themes: "blue" (standard), "green", "dark-blue"

class MainWindow(customtkinter.CTk):
    def __init__(self):
        super().__init__()
