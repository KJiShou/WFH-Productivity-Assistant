import calendar
import datetime as dt
import re
import tkinter as tk
from typing import Optional

import customtkinter as ctk

from app.utils.theme import WHITE_COLOR, BLACK_COLOR
from app.controllers.task_manager_controller import DATE_FMT

# ---------- helpers ----------
_HEX6 = re.compile(r"^#[0-9a-fA-F]{6}$")


def _hex(color: Optional[str]) -> Optional[str]:
    return color if isinstance(color, str) and _HEX6.match(color.strip()) else None


def _pill(master, text, bg, on_click=None):
    btn = ctk.CTkButton(
        master,
        text=text,
        height=26,
        corner_radius=12,
        fg_color=bg,
        text_color=BLACK_COLOR,
        hover_color=bg,
        command=on_click if on_click else lambda: None,
    )
    return btn


# ===================== Date Picker =====================
class _CalendarPopup(ctk.CTkToplevel):
    """Internal popup calendar used by DatePicker."""

    def __init__(self, master, init_date: dt.date, on_pick):
        super().__init__(master)
        self.title("Choose date")
        self.geometry("320x320")
        self.resizable(False, False)
        self.attributes("-topmost", True)
        self.grab_set()

        self._view = dt.date(init_date.year, init_date.month, 1)
        self._on_pick = on_pick

        self.grid_columnconfigure(0, weight=1)
        self._build()

    def _build(self):
        for w in self.winfo_children():
            w.destroy()

        head = ctk.CTkFrame(self, fg_color="transparent")
        head.grid(row=0, column=0, sticky="ew", padx=8, pady=(8, 4))
        ctk.CTkLabel(
            head, text=self._view.strftime("%B, %Y"), font=("Inter", 14, "bold")
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
        grid.grid(row=1, column=0, sticky="nsew", padx=8, pady=(4, 8))

        for i, wd in enumerate(["M", "T", "W", "T", "F", "S", "S"]):
            ctk.CTkLabel(
                grid, text=wd, font=("Inter", 12, "bold"), text_color=WHITE_COLOR
            ).grid(row=0, column=i, padx=6, pady=6)

        cal = calendar.Calendar(firstweekday=0)
        r = 1
        today = dt.date.today()
        for week in cal.monthdatescalendar(self._view.year, self._view.month):
            for c, d in enumerate(week):
                cmd_date = d
                btn = ctk.CTkButton(
                    grid,
                    text=str(d.day),
                    width=36,
                    height=28,
                    fg_color="#2F2F2F" if d.month != self._view.month else "#2A2A2A",
                    text_color=(
                        WHITE_COLOR if d.month == self._view.month else "#BDBDBD"
                    ),
                    hover_color="#4D4D4D",
                    command=lambda dd=cmd_date: self._pick(dd),
                )
                if d == today:
                    btn.configure(border_width=2, border_color=WHITE_COLOR)
                btn.grid(row=r, column=c, padx=4, pady=4)
            r += 1

    def _pick(self, date_: dt.date):
        self._on_pick(date_)
        self.destroy()

    def _prev(self):
        y, m = self._view.year, self._view.month
        m = 12 if m == 1 else m - 1
        y = y - 1 if m == 12 else y
        self._view = dt.date(y, m, 1)
        self._build()

    def _next(self):
        y, m = self._view.year, self._view.month
        m = 1 if m == 12 else m + 1
        y = y + 1 if m == 1 else y
        self._view = dt.date(y, m, 1)
        self._build()


class DatePicker(ctk.CTkFrame):
    """Readonly field with a calendar popup to choose a date."""

    def __init__(self, master, initial: Optional[dt.date] = None):
        super().__init__(master, fg_color="transparent")
        self._date: Optional[dt.date] = initial
        self._var = tk.StringVar(value=self._fmt(self._date))

        self.entry = ctk.CTkEntry(self, textvariable=self._var, state="readonly")
        self.entry.pack(side="left", fill="x", expand=True)

        ctk.CTkButton(
            self,
            text="📅",
            width=40,
            height=30,
            corner_radius=8,
            fg_color="#3F3F3F",
            text_color=WHITE_COLOR,
            hover_color="#5D5D5D",
            command=self._open,
        ).pack(side="left", padx=(8, 0))

    def _fmt(self, d: Optional[dt.date]) -> str:
        return d.strftime(DATE_FMT) if d else ""

    def _open(self):
        base = self._date or dt.date.today()
        _CalendarPopup(self, base, on_pick=self.set_date)

    def set_date(self, d: dt.date):
        self._date = d
        self._var.set(self._fmt(self._date))

    def set_from_str(self, s: Optional[str]):
        if not s:
            self._date = None
            self._var.set("")
            return
        try:
            self.set_date(dt.datetime.strptime(s, DATE_FMT).date())
        except ValueError:
            self._date = None
            self._var.set("")

    def get_date(self) -> Optional[dt.date]:
        return self._date

    def get_date_str(self) -> Optional[str]:
        return self._fmt(self._date) or None
