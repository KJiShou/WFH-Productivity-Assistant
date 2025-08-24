import customtkinter as ctk
from datetime import datetime, timedelta

from app.utils.theme import FONT_HEADER, TITLE_TEXT_COLOR


class SchedulePage(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color="transparent")
        # 整体布局（本页填满父容器）
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)


        # 顶部标题
        ctk.CTkLabel(
            self, text="Schedule",
            font=FONT_HEADER,
            text_color=TITLE_TEXT_COLOR
        ).grid(row=0, column=0, sticky="w", padx=10, pady=10)

        # 背景容器
        background = ctk.CTkFrame(
            self,
            fg_color="#555555",
            corner_radius=10
        )
        background.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)

        # 配置 background 可伸缩
        background.grid_rowconfigure(3, weight=1)  # 内容区可扩展
        background.grid_columnconfigure(0, weight=1)

        # 标题
        ctk.CTkLabel(
            background,
            text="My Calendar",
            text_color="white",
            font=("Times New Roman", 20, "bold", "underline")
        ).grid(row=0, column=0, pady=10)

        # 按钮区
        button_frame = ctk.CTkFrame(background, fg_color="transparent")
        button_frame.grid(row=1, column=0, pady=5)

        day_button = ctk.CTkButton(
            button_frame, text="Day",
            fg_color="transparent", hover_color="white",
            font=("Times New Roman", 20, "bold"),
            command=lambda: self.show_view("day")
        )
        day_button.grid(row=0, column=0, padx=20)

        week_button = ctk.CTkButton(
            button_frame, text="Week",
            fg_color="transparent", hover_color="white",
            font=("Times New Roman", 20, "bold"),
            command=lambda: self.show_view("week")
        )
        week_button.grid(row=0, column=1, padx=20)

        month_button = ctk.CTkButton(
            button_frame, text="Month",
            fg_color="transparent", hover_color="white",
            font=("Times New Roman", 20, "bold"),
            command=lambda: self.show_view("month")
        )
        month_button.grid(row=0, column=2, padx=20)

        # 显示月份栏
        display_frame = ctk.CTkFrame(
            background,
            fg_color="white",
            border_width=1,
            border_color="black"
        )
        display_frame.grid(row=2, column=0, pady=10, sticky="ew", padx=50)

        display_frame.grid_columnconfigure(0, weight=1)
        display_frame.grid_columnconfigure(1, weight=0)
        display_frame.grid_columnconfigure(2, weight=1)

        prev_btn = ctk.CTkButton(
            display_frame, text="<",
            fg_color="transparent",
            width=30,
            height=30,
            border_width=1,
            border_color="black",
            corner_radius=0,
            font=("Times New Roman", 20, "bold"),
            text_color="black",
            command=self.prev_day
        )
        prev_btn.grid(row=0, column=0, sticky="w",)

        self.display_date_var = ctk.StringVar()
        self.display_date_var.set(datetime.now().strftime("%d %B %Y"))

        self.display_label = ctk.CTkLabel(
            display_frame,
            textvariable=self.display_date_var,
            text_color="black",
            font=("Times New Roman", 20, "bold")
        ).grid(row=0, column=1)

        next_btn = ctk.CTkButton(
            display_frame, text=">",
            fg_color="transparent",
            width=30,
            height=30,
            border_width=1,
            border_color="black",
            corner_radius=0,
            font=("Times New Roman", 20, "bold"),
            text_color="black",
            command=self.next_day
        )
        next_btn.grid(row=0, column=2, sticky="e")

        # ---------- 内容区（day/week/month） ----------
        self.view_container = ctk.CTkFrame(background, fg_color="transparent")
        self.view_container.grid(row=3, column=0, sticky="nsew", padx=10, pady=10)

        # 让 view_container 内部可伸缩
        self.view_container.grid_rowconfigure(0, weight=1)
        self.view_container.grid_columnconfigure(0, weight=1)

        # 三个子视图（统一用 grid）
        self.day_frame = ctk.CTkFrame(self.view_container, fg_color="transparent")
        self.week_frame = ctk.CTkFrame(self.view_container, fg_color="transparent")
        self.month_frame = ctk.CTkFrame(self.view_container, fg_color="transparent")

        # -------- Day View --------
        timeline = ctk.CTkScrollableFrame(
            self.day_frame,
            fg_color="transparent"
        )
        timeline.pack(fill="both", expand=True, padx=10, pady=10)

        for hour in range(24):
            ctk.CTkLabel(
                timeline,
                text=f"{hour:02d}:00",
                font=("Times New Roman", 12),
                text_color="grey",
                width=80
            ).grid(row=hour, column=0, sticky="nsew", padx=5, pady=2)

            slot = ctk.CTkFrame(
                timeline,
                fg_color="white",
                border_width=2,
                border_color="black",
                height=50
            )
            slot.grid(row=hour, column=1, sticky="nsew", padx=(0, 5))
            slot.bind("<Button-1>", lambda e, h=hour: self.add_event(e, h))

        timeline.grid_columnconfigure(0, weight=0, minsize=80)
        timeline.grid_columnconfigure(1, weight=1)

        # -------- Week View --------
        week_container = ctk.CTkFrame(self.week_frame, fg_color="transparent")
        week_container.pack(fill="both", expand=True)

        # 改成 grid 控制布局：row 0 是 header，row 1 是 scroll
        week_container.grid_rowconfigure(0, minsize=60)  # 固定 header 高度
        week_container.grid_rowconfigure(1, weight=1)  # scroll_area 占剩余空间
        week_container.grid_columnconfigure(0, weight=1)

        # Header
        header_frame = ctk.CTkFrame(week_container, fg_color="transparent")
        header_frame.grid(row=0, column=0, sticky="ew")  # 🚨 用 grid 代替 pack
        header_frame.grid_propagate(False)  # 不允许内容撑开
        header_frame.configure(height=60)
        header_frame.grid_rowconfigure(0, weight=1)# 高度固定

        empty = ctk.CTkFrame(header_frame, fg_color="transparent", width=60, height=30)
        empty.grid(row=0, column=0, sticky="ew")

        days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        dates = ["18", "19", "20", "21", "22", "23", "24"]

        for i, (day, date) in enumerate(zip(days, dates), start=1):
            header = ctk.CTkFrame(
                header_frame,
                fg_color="white",
                border_width=2,
                border_color="black",
                width=100,
                height=40  # ✅ 改小
            )
            header.grid(row=0, column=i, sticky="nsew")

            ctk.CTkLabel(header, text=day,
                         font=("Times New Roman", 16, "bold"),
                         text_color="black").place(relx=0.5, rely=0.3, anchor="center")
            ctk.CTkLabel(header, text=date,
                         font=("Times New Roman", 12),
                         text_color="black").place(relx=0.5, rely=0.7, anchor="center")
        for i in range(1, 8):
            header_frame.grid_columnconfigure(i, weight=1)

        scrollbar_placeholder = ctk.CTkFrame(header_frame, fg_color="transparent", width=20)
        scrollbar_placeholder.grid(row=0, column=8, sticky="ew")

        # Scrollable 时间表
        scroll_area = ctk.CTkScrollableFrame(week_container, fg_color="transparent")
        scroll_area.grid(row=1, column=0, sticky="nsew")  # ✅ 用 grid，不再用 pack

        for hour in range(24):
            ctk.CTkLabel(
                scroll_area,
                text=f"{hour:02d}:00",
                font=("Times New Roman", 12),
                text_color="white"
            ).grid(row=hour, column=0, sticky="nsew")

            for i in range(1, 8):
                cell = ctk.CTkFrame(
                    scroll_area,
                    fg_color="white",
                    border_width=1,
                    border_color="black",
                    width=100,
                    height=40
                )
                cell.grid(row=hour, column=i, sticky="nsew")

        scroll_area.grid_columnconfigure(0, weight=0, minsize=60)
        for i in range(1, 8):
            scroll_area.grid_columnconfigure(i, weight=1)

        # -------- Month View --------
        month_container = ctk.CTkFrame(self.month_frame, fg_color="transparent")
        month_container.pack(fill="both", expand=True, padx=10, pady=10)

        # 星期标题
        header_frame = ctk.CTkFrame(month_container, fg_color="transparent")
        header_frame.pack(fill="x")

        days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        for i, day in enumerate(days):
            header = ctk.CTkFrame(
                header_frame,
                fg_color="white",
                border_width=2,
                border_color="black",
                width=100,
                height=60
            )
            header.grid(row=0, column=i, sticky="nsew")
            ctk.CTkLabel(header, text=day,
                         font=("Times New Roman", 15, "bold"),
                         text_color="black").place(relx=0.5, rely=0.5, anchor="center")

        for i in range(7):
            header_frame.grid_columnconfigure(i, weight=1)

        # 日历格子
        calendar_frame = ctk.CTkFrame(month_container, fg_color="white")
        calendar_frame.pack(fill="both", expand=True)

        start_day = 1  # 周二开始
        days_in_month = 31
        day_num = 1

        for row in range(6):
            for col in range(7):
                cell = ctk.CTkFrame(
                    calendar_frame,
                    fg_color="transparent",
                    border_width=2,
                    border_color="black",
                    width=100,
                    height=80
                )
                cell.grid(row=row, column=col, sticky="nsew")

                if (row == 0 and col < start_day) or day_num > days_in_month:
                    continue

                ctk.CTkLabel(
                    cell,
                    text=str(day_num),
                    font=("Times New Roman", 12, "bold"),
                    text_color="black"
                ).place(relx=0.05, rely=0.05, anchor="nw")

                day_num += 1

        for i in range(7):
            calendar_frame.grid_columnconfigure(i, weight=1)

        # 默认显示 month
        self.current_view = None
        self.show_view("month")

    def show_view(self, view_name: str):
        """切换视图"""
        if self.current_view:
            self.current_view.grid_forget()

        if view_name == "day":
            self.day_frame.grid(row=0, column=0, sticky="nsew")
            self.current_view = self.day_frame
        elif view_name == "week":
            self.week_frame.grid(row=0, column=0, sticky="nsew")
            self.current_view = self.week_frame
        elif view_name == "month":
            self.month_frame.grid(row=0, column=0, sticky="nsew")
            self.current_view = self.month_frame

    def prev_day(self):
        current = datetime.strptime(self.display_date_var.get(), "%d %B %Y")
        new_date = current - timedelta(days=1)
        self.display_date_var.set(new_date.strftime("%d %B %Y"))

    def next_day(self):
        current = datetime.strptime(self.display_date_var.get(), "%d %B %Y")
        new_date = current + timedelta(days=1)
        self.display_date_var.set(new_date.strftime("%d %B %Y"))

    def add_event(self, event, hour):
        popup = ctk.CTkToplevel(self)
        popup.title(f"New Event at {hour:02d}:00")
        popup.geometry("500x300")
        popup.attributes("-topmost", True)

        ctk.CTkLabel(popup, text="Title:").pack(pady=(20, 5), anchor="w", padx=20)
        title_entry = ctk.CTkEntry(popup, width=300, placeholder_text="Event title")
        title_entry.pack(pady=5, padx=20)

        ctk.CTkLabel(popup, text="Description:").pack(pady=(20, 5), anchor="w", padx=20)
        desc_entry = ctk.CTkTextbox(popup, width=300, height=80)
        desc_entry.pack(pady=5, padx=20)

        def save():
            title = title_entry.get().strip()
            desc = desc_entry.get("1.0", "end").strip()
            if title:
                label = ctk.CTkLabel(event.widget, text=title, text_color="blue", fg_color="white")
                label.place(relx=0.5, rely=0.5, anchor="center")

                # 🔹 点击 label 显示详情
                def show_details(e):
                    detail_win = ctk.CTkToplevel(self)
                    detail_win.title("Event Details")
                    detail_win.geometry("500x300")
                    detail_win.attributes("-topmost", True)

                    ctk.CTkLabel(detail_win, text=f"Title: {title}", font=("Times New Roman", 16, "bold")).pack(pady=10)
                    ctk.CTkLabel(detail_win, text=f"Description:\n{desc}", font=("Times New Roman", 12),
                                 justify="left").pack(pady=10)

                label.bind("<Button-1>", show_details)

            popup.destroy()

        ctk.CTkButton(popup, text="Save", command=save).pack(pady=20)




