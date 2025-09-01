import calendar
import datetime as dt
from typing import Optional

import customtkinter as ctk

from app.utils.theme import WHITE_COLOR


# Interactive calendar widget for date selection
class CalendarCard(ctk.CTkFrame):
    def __init__(self, master, when: Optional[dt.date] = None, on_select=None):
        super().__init__(master, corner_radius=18, fg_color="#4B4B4B")
        self.when = when or dt.date.today()
        self.on_select = on_select
        self.selected: Optional[dt.date] = None
        self.grid_columnconfigure(0, weight=1)
        self._build()

    def _build(self):
        for w in self.winfo_children():
            w.destroy()

        head = ctk.CTkFrame(self, fg_color="transparent")
        head.grid(row=0, column=0, sticky="ew", padx=10, pady=(10, 6))
        ctk.CTkLabel(
            head, text=self.when.strftime("%B, %Y"), font=("Inter", 14, "bold")
        ).pack(side="left")

        nav = ctk.CTkFrame(head, fg_color="transparent")
        nav.pack(side="right")
        ctk.CTkButton(
            nav,
            text="◀",
            width=36,
            fg_color="#3F3F3F",
            text_color=WHITE_COLOR,
            hover_color="#5D5D5D",
            command=self._prev,
        ).pack(side="left", padx=2)
        ctk.CTkButton(
            nav,
            text="▶",
            width=36,
            fg_color="#3F3F3F",
            text_color=WHITE_COLOR,
            hover_color="#5D5D5D",
            command=self._next,
        ).pack(side="left", padx=2)

        grid = ctk.CTkFrame(self, fg_color="#3F3F3F", corner_radius=12)
        grid.grid(row=1, column=0, sticky="nsew", padx=10, pady=(4, 10))

        for i, wd in enumerate(["M", "T", "W", "T", "F", "S", "S"]):
            ctk.CTkLabel(
                grid, text=wd, font=("Inter", 12, "bold"), text_color=WHITE_COLOR
            ).grid(row=0, column=i, padx=6, pady=6)

        cal = calendar.Calendar(firstweekday=0)
        r = 1
        for week in cal.monthdatescalendar(self.when.year, self.when.month):
            for c, d in enumerate(week):
                cmd_date = d
                btn = ctk.CTkButton(
                    grid,
                    text=str(d.day),
                    width=36,
                    height=28,
                    fg_color="#2F2F2F" if d.month != self.when.month else "#2A2A2A",
                    text_color=WHITE_COLOR if d.month == self.when.month else "#BDBDBD",
                    hover_color="#4D4D4D",
                    command=lambda dd=cmd_date: self._select(dd),
                )
                if self.selected and d == self.selected:
                    btn.configure(border_width=2, border_color=WHITE_COLOR)
                btn.grid(row=r, column=c, padx=4, pady=4)
            r += 1

    def _select(self, day: dt.date):
        if self.selected == day:
            self.selected = None
            if self.on_select:
                self.on_select(None)
        else:
            self.selected = day
            if self.on_select:
                self.on_select(day)
        self._build()

    def _prev(self):
        y, m = self.when.year, self.when.month
        m = 12 if m == 1 else m - 1
        y = y - 1 if m == 12 else y
        self.when = dt.date(y, m, 1)
        self._build()

    def _next(self):
        y, m = self.when.year, self.when.month
        m = 1 if m == 12 else m + 1
        y = y + 1 if m == 1 else y
        self.when = dt.date(y, m, 1)
        self._build()
