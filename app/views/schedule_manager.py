import customtkinter as ctk
import json, os
from datetime import datetime, timedelta

from app.utils.theme import FONT_HEADER, TITLE_TEXT_COLOR


class SchedulePage(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color="transparent")

        self.events = {}
        self.slots = {}
        self.week_slots = {}
        self.data_file = "events.json"
        self.load_events()

        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            self, text="Schedule",
            font=FONT_HEADER,
            text_color=TITLE_TEXT_COLOR
        ).grid(row=0, column=0, sticky="w", padx=10, pady=10)

        background = ctk.CTkFrame(
            self,
            fg_color="#555555",
            corner_radius=10
        )
        background.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)

        background.grid_rowconfigure(3, weight=1)  # 内容区可扩展
        background.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            background,
            text="My Calendar",
            text_color="white",
            font=("Times New Roman", 20, "bold", "underline")
        ).grid(row=0, column=0, pady=10)

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

        self.display_frame = ctk.CTkFrame(
            background,
            fg_color="white",
            border_width=1,
            border_color="black"
        )
        self.display_frame.grid(row=2, column=0, pady=10, sticky="ew", padx=50)

        self.display_frame.grid_columnconfigure(0, weight=1)
        self.display_frame.grid_columnconfigure(1, weight=0)
        self.display_frame.grid_columnconfigure(2, weight=1)

        prev_btn = ctk.CTkButton(
            self.display_frame, text="<",
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
        self.display_date_var.set(datetime.now().strftime("%Y-%m-%d"))

        self.display_label = ctk.CTkLabel(
            self.display_frame,
            textvariable=self.display_date_var,
            text_color="black",
            font=("Times New Roman", 20, "bold")
        )
        self.display_label.grid(row=0, column=1)

        next_btn = ctk.CTkButton(
            self.display_frame, text=">",
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

        self.view_container = ctk.CTkFrame(background, fg_color="transparent")
        self.view_container.grid(row=3, column=0, sticky="nsew", padx=10, pady=10)

        self.view_container.grid_rowconfigure(0, weight=1)
        self.view_container.grid_columnconfigure(0, weight=1)

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
                text_color="grey", width=80
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
            self.slots[hour] = slot
            timeline.grid_columnconfigure(0, weight=0, minsize=80)
            timeline.grid_columnconfigure(1, weight=1)

        # -------- Week View --------
        week_container = ctk.CTkFrame(self.week_frame, fg_color="transparent")
        week_container.pack(fill="both", expand=True)

        week_container.grid_rowconfigure(0, minsize=60)
        week_container.grid_rowconfigure(1, weight=1)
        week_container.grid_columnconfigure(0, weight=1)

        header_frame = ctk.CTkFrame(week_container, fg_color="transparent")
        header_frame.grid(row=0, column=0, sticky="ew")
        header_frame.grid_propagate(False)
        header_frame.configure(height=60)
        header_frame.grid_rowconfigure(0, weight=1)

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
                height=40
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

        scroll_area = ctk.CTkScrollableFrame(week_container, fg_color="transparent")
        scroll_area.grid(row=1, column=0, sticky="nsew")

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

        calendar_frame = ctk.CTkFrame(month_container, fg_color="white")
        calendar_frame.pack(fill="both", expand=True)

        start_day = 1
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


        self.current_view = None
        self.show_view("day")

    def prev_day(self):
        current = datetime.strptime(self.display_date_var.get(), "%Y-%m-%d")
        new_date = current - timedelta(days=1)
        self.display_date_var.set(new_date.strftime("%Y-%m-%d"))
        self.build_day_view()

    def next_day(self):
        current = datetime.strptime(self.display_date_var.get(), "%Y-%m-%d")
        new_date = current + timedelta(days=1)
        self.display_date_var.set(new_date.strftime("%Y-%m-%d"))
        self.build_day_view()

    def show_view(self, view_name: str):
        if self.current_view:
            self.current_view.grid_forget()

        if view_name == "day":
            self.day_frame.grid(row=0, column=0, sticky="nsew")
            self.current_view = self.day_frame
            self.build_day_view()
        elif view_name == "week":
            self.week_frame.grid(row=0, column=0, sticky="nsew")
            self.current_view = self.week_frame
        elif view_name == "month":
            self.month_frame.grid(row=0, column=0, sticky="nsew")
            self.current_view = self.month_frame


    def save_events(self):
        with open(self.data_file, "w", encoding="utf-8") as f:
            json.dump(self.events, f, ensure_ascii=False, indent=2)

    def load_events(self):
        if os.path.exists(self.data_file):
            with open(self.data_file, "r", encoding="utf-8") as f:
                self.events = json.load(f)
        else:
            self.events = {}


    def add_event(self, event, hour):
        popup = ctk.CTkToplevel(self)
        popup.title("Add Event")
        popup.geometry("500x400")
        popup.attributes("-topmost", True)

        ctk.CTkLabel(popup, text="Title:").pack(pady=5)
        title_entry = ctk.CTkEntry(popup, width=250)
        title_entry.pack(pady=5)

        ctk.CTkLabel(popup, text="Description:").pack(pady=5)
        desc_entry = ctk.CTkTextbox(popup, width=250, height=60)
        desc_entry.pack(pady=5)

        def save():
            title = title_entry.get()
            desc = desc_entry.get("1.0", "end").strip()
            if not title:
               popup.destroy()
               return

            date_key = self.display_date_var.get()
            event_data = {"hour": hour, "title": title, "desc": desc}

            self.events.setdefault(date_key, []).append(event_data)
            self.save_events()
            popup.destroy()
            self.build_day_view()
        ctk.CTkButton(popup, text="Save", command=save).pack(pady=10)


    def build_day_view(self):
        # 清空旧的事件（不销毁 slots 框架）
        for slot in self.slots.values():
            for widget in slot.winfo_children():
                widget.destroy()


        date_key = self.display_date_var.get()
        events = self.events.get(date_key, [])


        for ev in sorted(events, key=lambda x: x["hour"]):
            self.render_event(ev)

    def render_event(self, ev):
        hour = ev["hour"]
        slot = self.slots.get(hour)
        if slot:
            label = ctk.CTkLabel(
                slot,
                text=ev["title"],
                fg_color="lightblue",
                text_color="black"
            )
            label.pack(fill="both", expand=True, padx=2, pady=2)
            label.bind("<Button-1>", lambda e, ev=ev: self.show_detail(ev))

    def show_detail(self, ev):
         detail_win = ctk.CTkToplevel(self)
         detail_win.title("Event Details")
         detail_win.geometry("500x400")
         detail_win.attributes("-topmost", True)

         ctk.CTkLabel(detail_win, text="Title:", font=("Times New Roman", 14, "bold")).pack(pady=5)
         title_entry = ctk.CTkEntry(detail_win, width=250)
         title_entry.insert(0, ev["title"])
         title_entry.pack(pady=5)

         ctk.CTkLabel(detail_win, text="Description:", font=("Times New Roman", 14, "bold")).pack(pady=5)
         desc_entry = ctk.CTkTextbox(detail_win, width=250, height=100)
         desc_entry.insert("1.0", ev["desc"])
         desc_entry.pack(pady=5)

         def save_changes():
             date_key = self.display_date_var.get()
             ev["title"] = title_entry.get()
             ev["desc"] = desc_entry.get("1.0", "end").strip()
             self.save_events()
             detail_win.destroy()
             self.build_day_view()

         def delete_event():
            date_key = self.display_date_var.get()
            self.events[date_key].remove(ev)
            self.save_events()
            detail_win.destroy()
            self.build_day_view()

         ctk.CTkButton(detail_win, text="Save", fg_color="blue", command=save_changes).pack(pady=5)
         ctk.CTkButton(detail_win, text="Delete", fg_color="red", command=delete_event).pack(pady=5)


