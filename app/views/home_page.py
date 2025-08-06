import customtkinter as ctk
from app.utils.theme import (
    TEXT_COLOR,
    FONT_HEADER,
    BACKGROUND_COLOR,
    PRIMARY_SIDEBAR_COLOR,
    TERTIARY_SIDEBAR_COLOR,
    SECONDARY_SIDEBAR_COLOR,
    FONT_NORMAL,
    FONT_SMALL,
    TITLE_TEXT_COLOR,
    USER_FRAME_COLOR,
    TIME_FONT,
    SIDEBAR_HOVER_COLOR,
)


class MainView(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color=BACKGROUND_COLOR)

        self.create_sidebar()
        self.create_main()

    def create_sidebar(self):
        # create sidebar with layer
        self.sidebar3 = ctk.CTkFrame(
            master=self, fg_color=TERTIARY_SIDEBAR_COLOR, width=260
        )
        self.sidebar3.pack(side="left", fill="y", padx=0, pady=0)
        self.sidebar3.pack_propagate(False)

        self.sidebar2 = ctk.CTkFrame(
            master=self.sidebar3, fg_color=SECONDARY_SIDEBAR_COLOR, width=255
        )
        self.sidebar2.pack(side="left", fill="y", padx=0, pady=0)
        self.sidebar2.pack_propagate(False)

        self.sidebar = ctk.CTkFrame(
            master=self.sidebar2, fg_color=PRIMARY_SIDEBAR_COLOR, width=250
        )
        self.sidebar.pack(side="left", fill="y", padx=0, pady=0)
        self.sidebar.pack_propagate(False)

        # Welcome text
        self.welcome_label = ctk.CTkLabel(
            self.sidebar, text="Welcome,", font=FONT_NORMAL, text_color=TEXT_COLOR
        )
        self.welcome_label.pack(anchor="nw", padx=15, pady=(10, 0))

        self.user_frame = ctk.CTkFrame(
            self.sidebar, fg_color=USER_FRAME_COLOR, height=60
        )
        self.user_frame.pack(pady=(10, 20), padx=10, fill="x")
        self.user_frame.pack_propagate(False)

        self.user_label = ctk.CTkLabel(
            self.user_frame, text="User", font=FONT_NORMAL, text_color=TITLE_TEXT_COLOR
        )
        self.user_label.pack(pady=15, padx=15, anchor="w")

        btn = ctk.CTkButton(
            self.sidebar,
            text="Dashboard",
            font=FONT_NORMAL,
            fg_color="transparent",
            hover_color=SIDEBAR_HOVER_COLOR,
            text_color=TEXT_COLOR,
            anchor="w",
            height=40,
        )
        btn.pack(pady=2, padx=20, fill="x")

        def on_enter(e):
            btn.configure(text_color=TITLE_TEXT_COLOR, fg_color=SIDEBAR_HOVER_COLOR)

        def on_leave(e):
            btn.configure(text_color=TEXT_COLOR, fg_color="transparent")

        btn.bind("<Enter>", on_enter)
        btn.bind("<Leave>", on_leave)

    def create_main(self):
        # Main content frame
        self.content_frame = ctk.CTkFrame(self, fg_color=BACKGROUND_COLOR)
        self.content_frame.pack(
            side="right", fill="both", expand=True, padx=10, pady=10
        )

        # Header frame
        self.header_frame = ctk.CTkFrame(
            self.content_frame, fg_color="transparent", height=80
        )
        self.header_frame.pack(fill="x", pady=(0, 10))
        self.header_frame.pack_propagate(False)

        # Current time label
        self.time_label = ctk.CTkLabel(
            self.header_frame,
            text="Today Is: Loading...",
            font=TIME_FONT,
            text_color=TITLE_TEXT_COLOR,
        )
        self.time_label.pack(anchor="nw", padx=10, pady=10)
