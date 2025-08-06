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
    WHITE_COLOR,
    QUIT_BUTTON_COLOR,
    QUIT_BUTTON_HOVER_COLOR,
)


class SidebarButton(ctk.CTkButton):
    def __init__(
        self,
        master,
        text,
        command=None,
        font=None,
        text_color="#FFFFFF",
        hover_text_color="#000000",
        fg_color="transparent",
        hover_color="#444444",
        corner_radius=15,
        height=50,
        anchor="w",
        **kwargs,
    ):
        super().__init__(
            master=master,
            text=text,
            command=command,
            font=font,
            text_color=text_color,
            fg_color=fg_color,
            hover_color=hover_color,
            corner_radius=corner_radius,
            height=height,
            anchor=anchor,
            **kwargs,
        )

        self.default_text_color = text_color
        self.hover_text_color = hover_text_color
        self.default_fg_color = fg_color
        self.hover_fg_color = hover_color

        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)

        self.pack(pady=2, padx=5, fill="x")

    def _on_enter(self, event=None):
        self.configure(text_color=self.hover_text_color, fg_color=self.hover_fg_color)

    def _on_leave(self, event=None):
        self.configure(
            text_color=self.default_text_color, fg_color=self.default_fg_color
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

        dashboard_btn = SidebarButton(
            self.sidebar,
            text="Dashboard",
            font=FONT_NORMAL,
            text_color=TEXT_COLOR,
            hover_text_color=TITLE_TEXT_COLOR,
            hover_color=SIDEBAR_HOVER_COLOR,
        )

        task_btn = SidebarButton(
            self.sidebar,
            text="Task",
            font=FONT_NORMAL,
            text_color=TEXT_COLOR,
            hover_text_color=TITLE_TEXT_COLOR,
            hover_color=SIDEBAR_HOVER_COLOR,
        )

        calender_btn = SidebarButton(
            self.sidebar,
            text="Calendar",
            font=FONT_NORMAL,
            text_color=TEXT_COLOR,
            hover_text_color=TITLE_TEXT_COLOR,
            hover_color=SIDEBAR_HOVER_COLOR,
        )

        app_usage_btn = SidebarButton(
            self.sidebar,
            text="App Usage",
            font=FONT_NORMAL,
            text_color=TEXT_COLOR,
            hover_text_color=TITLE_TEXT_COLOR,
            hover_color=SIDEBAR_HOVER_COLOR,
        )

        settings_btn = SidebarButton(
            self.sidebar,
            text="Settings",
            font=FONT_NORMAL,
            text_color=TEXT_COLOR,
            hover_text_color=TITLE_TEXT_COLOR,
            hover_color=SIDEBAR_HOVER_COLOR,
        )

        separator = ctk.CTkFrame(self.sidebar, fg_color=WHITE_COLOR, height=2)
        separator.pack(pady=10, padx=20, fill="x")

        projects_label = ctk.CTkLabel(
            self.sidebar, text="Projects", font=FONT_NORMAL, text_color=TEXT_COLOR
        )
        projects_label.pack(pady=(10, 5), padx=20, anchor="w")

        quit_btn = ctk.CTkButton(
            self.sidebar,
            text="Quit",
            font=FONT_NORMAL,
            fg_color=QUIT_BUTTON_COLOR,
            hover_color="#e67878",
            text_color=TITLE_TEXT_COLOR,
            height=40,
            command=self.quit_app,
        )
        quit_btn.pack(side="bottom", pady=20, padx=20, fill="x")

    def quit_app(self):
        self.quit()
        self.destroy()

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
