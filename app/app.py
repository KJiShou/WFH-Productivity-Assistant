import customtkinter as ctk
from app.views.home_page import MainView


def run_app():
    app = ctk.CTk()
    app.geometry("600x400")
    app.title("My App")

    MainView(master=app).pack(fill="both", expand=True)

    app.mainloop()
