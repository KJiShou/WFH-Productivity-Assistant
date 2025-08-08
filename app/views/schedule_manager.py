import customtkinter as ctk

from app.utils.theme import FONT_HEADER, TITLE_TEXT_COLOR


class SchedulePage(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color="transparent")
        ctk.CTkLabel(
            self, text="Schedule", font=FONT_HEADER, text_color=TITLE_TEXT_COLOR
        ).pack(anchor="w", padx=10, pady=10)
