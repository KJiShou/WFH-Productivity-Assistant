from PIL import Image

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
    BLACK_COLOR,
)
from app.views.dashboard import DashboardPage
from app.views.schedule_manager import SchedulePage
from app.views.task_manager import TaskPage


class SidebarButton(ctk.CTkButton):
    def __init__(
        self,
        master,
        text,
        icon_light=None,
        icon_dark=None,
        command=None,
        font=None,
        text_color=TEXT_COLOR,
        hover_text_color=WHITE_COLOR,
        fg_color="transparent",
        hover_color=SIDEBAR_HOVER_COLOR,
        active_fg_color=SIDEBAR_HOVER_COLOR,
        active_text_color=BLACK_COLOR,
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

        # text configuration
        self.default_text_color = text_color
        self.hover_text_color = hover_text_color
        self.active_text_color = active_text_color

        # button fg color configuration
        self.default_fg_color = fg_color
        self.hover_fg_color = hover_color
        self.active_fg_color = active_fg_color

        # CTkImage objects for light/dark icons
        self.icon_light = icon_light
        self.icon_dark = icon_dark

        # flag for button active or not
        self._active = False

        # func for enter and leave
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)

        self.pack(pady=2, padx=5, fill="x")

    # check current focusing UI
    def set_active(self, active: bool):
        self._active = active
        if active:
            self.configure(
                text_color=self.active_text_color,
                fg_color=self.active_fg_color,
                border_width=2,
                border_color=self.hover_fg_color,
                image=self.icon_dark,
            )
        else:
            self.configure(
                text_color=self.default_text_color,
                fg_color=self.default_fg_color,
                border_width=0,
                image=self.icon_light,
            )

    # check mouse focus on the button
    def _on_enter(self, event=None):
        if not self._active:
            self.configure(
                text_color=self.hover_text_color,
                fg_color=self.hover_fg_color,
                image=(self.icon_dark),
            )

    # check mouse not focus on the button
    def _on_leave(self, event=None):
        if not self._active:
            self.configure(
                text_color=self.default_text_color,
                fg_color=self.default_fg_color,
                image=(self.icon_light),
            )


class MainView(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color=BACKGROUND_COLOR)
        # create sidebar and main frame
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

        # create button
        self.buttons = {}

        dashboard_icon_dark = ctk.CTkImage(
            Image.open("app/assets/dashboard_icon_black.png"),
            size=(20, 20),
        )
        dashboard_icon_light = ctk.CTkImage(
            Image.open("app/assets/dashboard_icon_white.png"),
            size=(20, 20),
        )
        dashboard_btn = SidebarButton(
            self.sidebar,
            text="Dashboard",
            icon_dark=dashboard_icon_dark,
            icon_light=dashboard_icon_light,
            font=FONT_NORMAL,
            text_color=TEXT_COLOR,
            hover_text_color=TITLE_TEXT_COLOR,
            hover_color=SIDEBAR_HOVER_COLOR,
            command=lambda: self.show_page("Dashboard"),
            image=dashboard_icon_light,
            compound="left",
            anchor="w",
        )
        self.buttons["Dashboard"] = dashboard_btn

        task_icon_dark = ctk.CTkImage(
            Image.open("app/assets/task_icon_black.png"),
            size=(20, 20),
        )
        task_icon_light = ctk.CTkImage(
            Image.open("app/assets/task_icon_white.png"),
            size=(20, 20),
        )

        task_btn = SidebarButton(
            self.sidebar,
            text="Task",
            font=FONT_NORMAL,
            text_color=TEXT_COLOR,
            hover_text_color=TITLE_TEXT_COLOR,
            hover_color=SIDEBAR_HOVER_COLOR,
            command=lambda: self.show_page("Task"),
            icon_dark=task_icon_dark,
            icon_light=task_icon_light,
            image=task_icon_light,
            compound="left",
            anchor="w",
        )

        self.buttons["Task"] = task_btn

        schedule_icon_dark = ctk.CTkImage(
            Image.open("app/assets/schedule_icon_black.png"),
            size=(20, 20),
        )
        schedule_icon_light = ctk.CTkImage(
            Image.open("app/assets/schedule_icon_white.png"),
            size=(20, 20),
        )

        schedule_btn = SidebarButton(
            self.sidebar,
            text="Schedule",
            font=FONT_NORMAL,
            text_color=TEXT_COLOR,
            hover_text_color=TITLE_TEXT_COLOR,
            hover_color=SIDEBAR_HOVER_COLOR,
            command=lambda: self.show_page("Schedule"),
            icon_dark=schedule_icon_dark,
            icon_light=schedule_icon_light,
            image=schedule_icon_light,
            compound="left",
            anchor="w",
        )

        self.buttons["Schedule"] = schedule_btn

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

    def show_page(self, name: str):
        page = self.pages.get(name)
        if page:
            page.tkraise()

        for key, btn in self.buttons.items():
            btn.set_active(key == name)

    def create_main(self):
        self.content_frame = ctk.CTkFrame(self, fg_color=BACKGROUND_COLOR)
        self.content_frame.pack(
            side="right", fill="both", expand=True, padx=10, pady=10
        )

        self.page_container = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        self.page_container.pack(fill="both", expand=True, padx=0, pady=0)

        # allow the page to expand
        self.page_container.grid_rowconfigure(0, weight=1)
        self.page_container.grid_columnconfigure(0, weight=1)

        # Pre-create pages and store in a dict
        self.pages = {
            "Dashboard": DashboardPage(self.page_container),
            "Task": TaskPage(self.page_container),
            "Schedule": SchedulePage(self.page_container),
        }
        for page in self.pages.values():
            page.grid(row=0, column=0, sticky="nsew")  # stack them

        # Start with dashboard
        self.show_page("Dashboard")
