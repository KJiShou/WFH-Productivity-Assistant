import customtkinter as ctk

from app.utils.theme import WIN_SIZE
from app.views.sidebar import MainView


def run_app():
    app = ctk.CTk()
    app.geometry(WIN_SIZE)
    app.title("WFH Productivity Assistant")

    MainView(master=app).pack(fill="both", expand=True)

    app.mainloop()
