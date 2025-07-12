import customtkinter as ctk
from app.utils.theme import PRIMARY_COLOR, FONT_HEADER


class MainView(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        label = ctk.CTkLabel(
            self, text="Dashboard", text_color=PRIMARY_COLOR, font=FONT_HEADER
        )
        label.pack(pady=10)
