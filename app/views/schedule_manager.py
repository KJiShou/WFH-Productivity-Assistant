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
        self.month_slots = {}
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

        background.grid_rowconfigure(3, weight=1)
        background.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            background,
            text="My Calendar",
            text_color="white",
            font=("Times New Roman", 20, "bold", "underline")
        ).grid(row=0, column=0, pady=10)

        button_frame = ctk.CTkFrame(background, fg_color="transparent")
        button_frame.grid(row=1, column=0, pady=5)

        self.day_button = ctk.CTkButton(
            button_frame, text="Day",
            fg_color="transparent", hover_color="white",
            font=("Times New Roman", 20, "bold"),
            command=lambda: self.show_view("day")
        )
        self.day_button.grid(row=0, column=0, padx=20)

        self.week_button = ctk.CTkButton(
            button_frame, text="Week",
            fg_color="transparent", hover_color="white",
            font=("Times New Roman", 20, "bold"),
            command=lambda: self.show_view("week")
        )
        self.week_button.grid(row=0, column=1, padx=20)

        self.month_button = ctk.CTkButton(
            button_frame, text="Month",
            fg_color="transparent", hover_color="white",
            font=("Times New Roman", 20, "bold"),
            command=lambda: self.show_view("month")
        )
        self.month_button.grid(row=0, column=2, padx=20)

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

        prev_button = ctk.CTkButton(
            self.display_frame, text="<",
            fg_color="transparent",
            width=30,
            height=30,
            border_width=1,
            border_color="black",
            corner_radius=0,
            font=("Times New Roman", 20, "bold"),
            text_color="black",
            command=self.prev_button
        )
        prev_button.grid(row=0, column=0, sticky="w",)

        self.display_date_var = ctk.StringVar()
        self.display_date_var.set(datetime.now().strftime("%Y-%m-%d"))

        self.display_label = ctk.CTkLabel(
            self.display_frame,
            textvariable=self.display_date_var,
            text_color="black",
            font=("Times New Roman", 20, "bold")
        )
        self.display_label.grid(row=0, column=1)

        next_button = ctk.CTkButton(
            self.display_frame, text=">",
            fg_color="transparent",
            width=30,
            height=30,
            border_width=1,
            border_color="black",
            corner_radius=0,
            font=("Times New Roman", 20, "bold"),
            text_color="black",
            command=self.next_button
        )
        next_button.grid(row=0, column=2, sticky="e")

        self.view_container = ctk.CTkFrame(background, fg_color="transparent")
        self.view_container.grid(row=3, column=0, sticky="nsew", padx=10, pady=10)

        self.view_container.grid_rowconfigure(0, weight=1)
        self.view_container.grid_columnconfigure(0, weight=1)

        self.day_frame = ctk.CTkFrame(self.view_container, fg_color="transparent")
        self.week_frame = ctk.CTkFrame(self.view_container, fg_color="transparent")
        self.month_frame = ctk.CTkFrame(self.view_container, fg_color="transparent")
        self.current_view = None
        self.show_view("day")

    def prev_button(self):
        current = datetime.strptime(self.display_date_var.get(), "%Y-%m-%d")
        new_date = current - timedelta(days=1)
        self.display_date_var.set(new_date.strftime("%Y-%m-%d"))

        if self.current_view == self.day_frame:
            self.build_day_view()
        elif self.current_view == self.week_frame:
            week_start = new_date - timedelta(days=new_date.weekday())
            self.build_week_view(week_start)
        elif self.current_view == self.month_frame:
            new_date = (current.replace(day=1) - timedelta(days=1)).replace(day=1)
            self.display_date_var.set(new_date.strftime("%Y-%m-%d"))
            self.build_month_view()

    def next_button(self):
        current = datetime.strptime(self.display_date_var.get(), "%Y-%m-%d")
        new_date = current + timedelta(days=1)
        self.display_date_var.set(new_date.strftime("%Y-%m-%d"))

        if self.current_view == self.day_frame:
            self.build_day_view()
        elif self.current_view == self.week_frame:
            week_start = new_date - timedelta(days=new_date.weekday())
            self.build_week_view(week_start)
        elif self.current_view == self.month_frame:
            next_month = current.replace(day=28) + timedelta(days=4)  # Always jumps to next month
            new_date = next_month.replace(day=1)
            self.display_date_var.set(new_date.strftime("%Y-%m-%d"))
            self.build_month_view()

    def show_view(self, view_name: str):
        if self.current_view:
            self.current_view.grid_forget()

        self.day_button.configure(fg_color="transparent", text_color="white")
        self.week_button.configure(fg_color="transparent", text_color="white")
        self.month_button.configure(fg_color="transparent", text_color="white")

        if view_name == "day":
            self.day_frame.grid(row=0, column=0, sticky="nsew")
            self.current_view = self.day_frame
            self.day_button.configure(fg_color="white", text_color="black")
            self.build_day_view()
        elif view_name == "week":
            self.week_frame.grid(row=0, column=0, sticky="nsew")
            self.current_view = self.week_frame
            self.week_button.configure(fg_color="white", text_color="black")
            self.build_week_view()
        elif view_name == "month":
            self.month_frame.grid(row=0, column=0, sticky="nsew")
            self.current_view = self.month_frame
            self.month_button.configure(fg_color="white", text_color="black")
            self.build_month_view()

    def build_day_view(self):
        for widget in self.day_frame.winfo_children():
            widget.destroy()

        timeline = ctk.CTkScrollableFrame(
            self.day_frame,
            fg_color="transparent"
        )
        timeline.pack(fill="both", expand=True, padx=10, pady=10)

        self.slots.clear()

        for hour in range(24):
            ctk.CTkLabel(
                timeline,
                text=f"{hour:02d}:00",
                font=("Times New Roman", 12),
                text_color="white",
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
            slot.bind("<Button-1>", lambda e, h=hour: self.add_event(h))

            self.slots[hour] = slot

            timeline.grid_columnconfigure(0, weight=0, minsize=80)
            timeline.grid_columnconfigure(1, weight=1)

        self.render_day_events()

    def render_day_events(self):
        for slot in self.slots.values():
            for widget in slot.winfo_children():
                widget.destroy()

        date_key = self.display_date_var.get()
        events = self.events.get(date_key, [])

        for ev in sorted(events, key=lambda x: x["hour"]):
            slot = self.slots.get(ev["hour"])
            if slot:
                label = ctk.CTkLabel(
                    slot,
                    text=ev["title"],
                    fg_color="lightblue",
                    text_color="black"
                )
                label.pack(fill="both", expand=True, padx=2, pady=2)
                label.bind("<Button-1>", lambda e, event=ev: self.show_detail(event))

    def build_week_view(self, week_start_date=None):
        self.week_frame.grid_rowconfigure(0, weight=0)
        self.week_frame.grid_rowconfigure(1, weight=1)
        self.week_frame.grid_columnconfigure(0, weight=1)

        if week_start_date is None:
            today = datetime.today()
            week_start_date = today - timedelta(days=today.weekday())

        self.week_slots.clear()

        for widget in self.week_frame.winfo_children():
            widget.destroy()

        header_frame = ctk.CTkFrame(self.week_frame, fg_color="transparent", height=40)
        header_frame.grid(row=0, column=0, sticky="ew")

        empty = ctk.CTkLabel(header_frame, text="", fg_color="transparent", width=60)
        empty.grid(row=0, column=0, sticky="nsew")

        days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        for i, day in enumerate(days,start=1):
            date = (week_start_date + timedelta(days=i-1)).strftime("%Y-%m-%d")
            lbl = ctk.CTkButton(
                header_frame,
                text=f"{day}\n{date}",
                fg_color="white",
                text_color="black",
                corner_radius=0,
                border_width=3,
                border_color="black",
                width=100,
                height=60,
                hover=False
            )
            lbl.grid(row=0, column=i, padx=1, pady=1, sticky="nsew")

            header_frame.grid_columnconfigure(i, weight=1)

        spacer = ctk.CTkLabel(header_frame, text="", fg_color="transparent", width=20)
        spacer.grid(row=0, column=8, sticky="nsew")

        header_frame.grid_columnconfigure(0, weight=1, minsize=70)
        header_frame.grid_columnconfigure(8, weight=0)

        scroll_area = ctk.CTkScrollableFrame(self.week_frame, fg_color="transparent")
        scroll_area.grid(row=1, column=0, sticky="nsew")

        for col in range(8):
            scroll_area.grid_columnconfigure(col, weight=1)

        for hour in range(24):
            scroll_area.grid_rowconfigure(hour, minsize=50)


            ctk.CTkLabel(scroll_area, text=f"{hour:02d}:00", text_color="white", width=60).grid(
                row=hour, column=0, sticky="nsew"
            )

            for i in range(7):
                date = (week_start_date + timedelta(days=i)).strftime("%Y-%m-%d")
                cell = ctk.CTkFrame(
                    scroll_area,
                    fg_color="white",
                    border_width=1,
                    border_color="black",
                    width=100,
                    height=50
                )
                cell.grid(row=hour, column=i + 1, padx=1, pady=1, sticky="nsew")
                cell.bind("<Button-1>", lambda e, h=hour, d=date: self.add_event(h, d))
                self.week_slots.setdefault(date, {})[hour] = cell
            ctk.CTkLabel(scroll_area, text="", fg_color="transparent").grid(row=hour, column=8, sticky="nsew")
        self.render_week_events()

    def render_week_events(self):
        for day_slots in self.week_slots.values():
            for cell in day_slots.values():
                for widget in cell.winfo_children():
                    widget.destroy()

        for date_key, events in self.events.items():
            if date_key in self.week_slots:
                for ev in events:
                    hour = ev["hour"]
                    if hour in self.week_slots[date_key]:
                        cell = self.week_slots[date_key][hour]
                        lbl = ctk.CTkLabel(cell, text=ev["title"], fg_color="lightblue", text_color="black")
                        lbl.pack(fill="both", expand=True, padx=1, pady=1)
                        lbl.bind("<Button-1>", lambda e, event=ev: self.show_detail(event))

    def build_month_view(self):
        self.month_slots.clear()
        for widget in self.month_frame.winfo_children():
            widget.destroy()

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

        current_date = datetime.strptime(self.display_date_var.get(), "%Y-%m-%d")
        year, month = current_date.year, current_date.month
        first_day = datetime(year, month, 1)
        start_weekday = first_day.weekday()  # 0=Mon
        if month == 12:
            days_in_month = 31
        else:
            days_in_month = (datetime(year, month + 1, 1) - timedelta(days=1)).day

        total_cells = start_weekday + days_in_month
        num_rows = (total_cells + 6) // 7
        day_num = 1

        for row in range(num_rows):
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

                if (row == 0 and col < start_weekday) or day_num > days_in_month:
                    continue

                ctk.CTkLabel(
                    cell,
                    text=str(day_num),
                    font=("Times New Roman", 14, "bold"),
                    text_color="black"
                ).place(relx=0.05, rely=0.05, anchor="nw")

                event_frame = ctk.CTkFrame(cell, fg_color="transparent")
                event_frame.place(relx=0.05, rely=0.35, relwidth=0.9, relheight=0.7)

                date_key = datetime(year, month, day_num).strftime("%Y-%m-%d")
                self.month_slots[date_key] = event_frame

                day_num += 1

        for i in range(7):
            calendar_frame.grid_columnconfigure(i, weight=1)
        for i in range(num_rows):
            calendar_frame.grid_rowconfigure(i, weight=1)

        self.render_month_events()

    def render_month_events(self):
        for date, frame in self.month_slots.items():
            for widget in frame.winfo_children():
                widget.destroy()

        for date, events in self.events.items():
            if date not in self.month_slots:
                continue

            container = self.month_slots[date]

            count = len(events)
            if count > 0:
                btn = ctk.CTkButton(
                    container,
                    text=f"{count} events",
                    fg_color="lightblue",
                    text_color="black",
                    width=100,
                    height=30,
                    command=lambda d=date: self.show_day_from_month(d)
                )
                btn.pack(anchor="center", pady=7)

    def show_day_from_month(self, date_str: str):
        self.display_date_var.set(date_str)
        self.show_view("day")

    def save_events(self):
        with open(self.data_file, "w", encoding="utf-8") as f:
            json.dump(self.events, f, ensure_ascii=False, indent=2)

    def load_events(self):
        if os.path.exists(self.data_file):
            with open(self.data_file, "r", encoding="utf-8") as f:
                self.events = json.load(f)
        else:
            self.events = {}


    def add_event(self, hour, date_key=None):
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

        if not date_key:
            date_key = self.display_date_var.get()

        def save():
            title = title_entry.get()
            desc = desc_entry.get("1.0", "end").strip()
            if not title:
               popup.destroy()
               return

            event_data = {"date": date_key, "hour": hour, "title": title, "desc": desc}
            self.events.setdefault(date_key, []).append(event_data)
            self.save_events()
            popup.destroy()

            if self.current_view == self.day_frame:
                self.build_day_view()
            elif self.current_view == self.week_frame:
                current_date = datetime.strptime(self.display_date_var.get(), "%Y-%m-%d")
                week_start = current_date - timedelta(days=current_date.weekday())
                self.build_week_view(week_start)
        ctk.CTkButton(popup, text="Save", command=save).pack(pady=10)


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
             ev["title"] = title_entry.get()
             ev["desc"] = desc_entry.get("1.0", "end").strip()
             self.save_events()
             detail_win.destroy()
             if self.current_view == self.day_frame:
                 self.build_day_view()
             elif self.current_view == self.week_frame:
                 current_date = datetime.strptime(self.display_date_var.get(), "%Y-%m-%d")
                 week_start = current_date - timedelta(days=current_date.weekday())
                 self.build_week_view(week_start)
             elif self.current_view == self.month_frame:
                 self.build_month_view()

         def delete_event():
             date_key = ev.get("date")
             if date_key in self.events:
                 self.events[date_key].remove(ev)
                 if not self.events[date_key]:
                     del self.events[date_key]
             self.save_events()
             detail_win.destroy()
             if self.current_view == self.day_frame:
                self.build_day_view()
             elif self.current_view == self.week_frame:
                current_date = datetime.strptime(self.display_date_var.get(), "%Y-%m-%d")
                week_start = current_date - timedelta(days=current_date.weekday())
                self.build_week_view(week_start)
             elif self.current_view == self.month_frame:
                self.build_month_view()

         ctk.CTkButton(detail_win, text="Save", fg_color="blue", command=save_changes).pack(pady=5)
         ctk.CTkButton(detail_win, text="Delete", fg_color="red", command=delete_event).pack(pady=5)


