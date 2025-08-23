import calendar
import datetime as dt
import re
import tkinter as tk
import tkinter.messagebox as msgbox
from typing import Optional

import customtkinter as ctk

from app.utils.theme import (
    FONT_HEADER,
    TITLE_TEXT_COLOR,
    WHITE_COLOR,
    BLACK_COLOR,
    BUTTON_COLOR,
    SELECT_BOX_COLOR,
)
from app.controllers.task_manager_controller import (
    TaskManagerController,
    Task,
    DATE_FMT,
)
from app.controllers.project_manager_controller import ProjectManagerController, Project
from app.views.pomodoro_timer import TimerPage

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


# ------------------ Add / Edit dialogs ------------------
class BaseTaskDialog(ctk.CTkToplevel):
    def __init__(self, master, title: str):
        super().__init__(master)
        self.title(title)
        self.geometry("520x480")
        self.resizable(False, False)
        self.grab_set()
        self.focus_force()
        self.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(self, text="Title").grid(
            row=0, column=0, padx=10, pady=(16, 8), sticky="w"
        )
        self.e_title = ctk.CTkEntry(self)
        self.e_title.grid(row=0, column=1, padx=10, pady=(16, 8), sticky="ew")

        ctk.CTkLabel(self, text="Description").grid(
            row=1, column=0, padx=10, pady=8, sticky="w"
        )
        self.e_desc = ctk.CTkTextbox(self, height=110)
        self.e_desc.grid(row=1, column=1, padx=10, pady=8, sticky="nsew")

        ctk.CTkLabel(self, text="Project").grid(
            row=2, column=0, padx=10, pady=8, sticky="w"
        )
        self.c_project = ctk.CTkOptionMenu(self, values=["(None)"])
        self.c_project.grid(row=2, column=1, padx=10, pady=8, sticky="w")

        ctk.CTkLabel(self, text="Due date").grid(
            row=3, column=0, padx=10, pady=8, sticky="w"
        )
        # >>> replace Entry with DatePicker
        self.dp_due = DatePicker(self)
        self.dp_due.grid(row=3, column=1, padx=10, pady=8, sticky="ew")

        ctk.CTkLabel(self, text="Status").grid(
            row=4, column=0, padx=10, pady=8, sticky="w"
        )
        self.c_status = ctk.CTkOptionMenu(self, values=["todo", "doing", "done"])
        self.c_status.grid(row=4, column=1, padx=10, pady=8, sticky="w")

        bar = ctk.CTkFrame(self, fg_color="transparent")
        bar.grid(row=5, column=0, columnspan=2, sticky="e", padx=10, pady=14)

        # Fixed: Added proper spacing between Cancel and Save buttons
        ctk.CTkButton(bar, text="Cancel", command=self.destroy).pack(side="right")
        self.ok_btn = ctk.CTkButton(bar, text="Save", command=self._save)
        self.ok_btn.pack(side="right", padx=(0, 16))  # Added 16px gap between buttons

    def set_projects(self, names: list[str], preselect: Optional[str] = None):
        values = ["(None)"] + names
        self.c_project.configure(values=values)
        if preselect and preselect in names:
            self.c_project.set(preselect)
        else:
            self.c_project.set(values[0])

    def _values(self):
        proj = self.c_project.get()
        if proj == "(None)":
            proj = None
        return dict(
            title=self.e_title.get().strip(),
            description=self.e_desc.get("1.0", "end").strip(),
            project=proj,
            due_date=self.dp_due.get_date_str(),  # <- from date picker
            status=self.c_status.get(),
        )

    def _save(self):  # override
        pass


class AddTaskDialog(BaseTaskDialog):
    def __init__(
        self,
        master,
        on_done,
        project_names: list[str],
        preset_date: Optional[dt.date] = None,
    ):
        super().__init__(master, "Add Task")
        self.on_done = on_done
        self.c_status.set("todo")
        self.set_projects(project_names)
        if preset_date:
            self.dp_due.set_date(preset_date)

    def _save(self):
        payload = self._values()
        if not payload["title"]:
            return
        self.on_done(payload)
        self.destroy()


class EditTaskDialog(BaseTaskDialog):
    def __init__(self, master, task: Task, on_done, project_names: list[str]):
        super().__init__(master, "Edit Task")
        self.task = task
        self.on_done = on_done
        self.e_title.insert(0, task.title)
        self.e_desc.insert("1.0", task.description or "")
        self.set_projects(project_names, preselect=task.project or None)
        self.dp_due.set_from_str(task.due_date)
        self.c_status.set(task.status)

    def _save(self):
        self.on_done(self.task.id, self._values())
        self.destroy()


# ------------------ Add Project dialog ------------------
class AddProjectDialog(ctk.CTkToplevel):
    def __init__(self, master, on_done):
        super().__init__(master)
        self.title("Add Project")
        self.geometry("420x250")
        self.resizable(False, False)
        self.grab_set()
        self.focus_force()

        ctk.CTkLabel(self, text="Project Name").pack(anchor="w", padx=12, pady=(14, 6))
        self.e_name = ctk.CTkEntry(self)
        self.e_name.pack(fill="x", padx=12)

        ctk.CTkLabel(self, text="Color (optional, e.g. #F7B4BB)").pack(
            anchor="w", padx=12, pady=(10, 6)
        )
        self.e_color = ctk.CTkEntry(self)
        self.e_color.pack(fill="x", padx=12)

        bar = ctk.CTkFrame(self, fg_color="transparent")
        bar.pack(fill="x", padx=12, pady=12)

        # Fixed: Added proper spacing between Cancel and Save buttons
        ctk.CTkButton(bar, text="Cancel", command=self.destroy).pack(side="right")
        ctk.CTkButton(
            bar,
            text="Save",
            command=lambda: (
                on_done(
                    self.e_name.get().strip() or "", self.e_color.get().strip() or None
                ),
                self.destroy(),
            ),
        ).pack(
            side="right", padx=(0, 16)
        )  # Added 16px gap between buttons


# ------------------ Calendar with white nav arrows (sidebar) ------------------
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
        # Enhanced: Toggle functionality - clicking the same date deselects it
        if self.selected == day:
            self.selected = None
            if self.on_select:
                self.on_select(None)  # Pass None to clear filter
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


# ------------------ Edit Project dialog ------------------
class EditProjectDialog(ctk.CTkToplevel):
    def __init__(self, master, project: Project, on_save):
        super().__init__(master)
        self.title(f"Edit Project")
        self.geometry("420x200")
        self.resizable(False, False)
        self.grab_set()
        self.focus_force()
        self.proj = project
        self.on_save = on_save

        ctk.CTkLabel(self, text="Project Name").pack(anchor="w", padx=12, pady=(14, 6))
        self.e_name = ctk.CTkEntry(self)
        self.e_name.pack(fill="x", padx=12)
        self.e_name.insert(0, project.name)

        ctk.CTkLabel(self, text="Color (#RRGGBB)").pack(
            anchor="w", padx=12, pady=(10, 6)
        )
        self.e_color = ctk.CTkEntry(self)
        self.e_color.pack(fill="x", padx=12)
        self.e_color.insert(0, project.color or "")

        bar = ctk.CTkFrame(self, fg_color="transparent")
        bar.pack(fill="x", padx=12, pady=12)

        ctk.CTkButton(
            bar, text="Delete", command=self._delete_project, fg_color="red"
        ).pack(side="right")
        ctk.CTkButton(bar, text="Cancel", command=self.destroy).pack(
            side="right", padx=(0, 16)
        )
        ctk.CTkButton(bar, text="Save", command=self._save).pack(
            side="right", padx=(0, 16)
        )

    def _save(self):
        name = self.e_name.get().strip()
        color = _hex(self.e_color.get().strip() or None)
        if not name:
            return
        self.on_save(self.proj, name, color)
        self.destroy()

    def _delete_project(self):
        # Confirm deletion
        if msgbox.askyesno(
            "Delete Project",
            f"Are you sure you want to delete '{self.proj.name}'?\n\nThis action cannot be undone.",
        ):
            self.on_save(self.proj, None, None)  # Signal deletion with None values
            self.destroy()


# ------------------ Task row (toggle + flat title + right-side chips) ------------------
class TaskItem(ctk.CTkFrame):
    def __init__(
        self,
        master,
        task: Task,
        proj_lookup: dict[str, Project],
        on_toggle,
        on_open_menu,
        on_edit_project,
    ):
        super().__init__(master, fg_color="transparent")
        self.task = task
        self._proj_lookup = proj_lookup
        self.on_toggle = on_toggle
        self.on_open_menu = on_open_menu
        self.on_edit_project = on_edit_project

        # left toggle (✓ when done)
        self.toggle = ctk.CTkButton(
            self,
            text="",
            width=26,
            height=26,
            corner_radius=13,
            fg_color="#2B2B2B",
            text_color=WHITE_COLOR,
            hover_color="#4A4A4A",
            command=self._toggle_click,
        )
        self.toggle.pack(side="left", padx=(10, 12), pady=6)

        # title (flat + hover bold)
        self.btn = ctk.CTkButton(
            self,
            text=self.task.title,
            fg_color="transparent",
            hover=False,
            text_color=WHITE_COLOR,
            anchor="w",
            font=("Inter", 13, "normal"),
            command=lambda: self.on_open_menu(self.task),
        )
        self.btn.pack(side="left", fill="x", expand=True, pady=4)
        self.btn.bind(
            "<Enter>", lambda e: self.btn.configure(font=("Inter", 13, "bold"))
        )
        self.btn.bind(
            "<Leave>", lambda e: self.btn.configure(font=("Inter", 13, "normal"))
        )

        # right side: project pill + date
        right = ctk.CTkFrame(self, fg_color="transparent")
        right.pack(side="right", padx=8)
        # project pill (click to edit project)
        if self.task.project:
            p = self._proj_lookup.get(self.task.project)
            color = _hex(p.color) if p else None
            pill_bg = color or SELECT_BOX_COLOR
            _pill(
                right,
                self.task.project,
                pill_bg,
                on_click=lambda: self.on_edit_project(self.task.project),
            ).pack(side="left", padx=(0, 16))
        # date
        ctk.CTkLabel(
            right,
            text=self.task.due_date or "",
            font=("Inter", 13, "bold"),
            text_color=WHITE_COLOR,
        ).pack(side="left")

        self._style_toggle()

    def _style_toggle(self):
        if self.task.status == "done":
            self.toggle.configure(fg_color="#2E7D32", text="✓")
        else:
            self.toggle.configure(fg_color="#2B2B2B", text="")

    def _toggle_click(self):
        new_status = "done" if self.task.status != "done" else "doing"
        self.task.status = new_status
        self._style_toggle()
        self.on_toggle(self.task.id, new_status)


# ------------------ Main Page ------------------
class TaskPage(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color="transparent")
        self.tm = TaskManagerController("tasks.json")
        self.pm = ProjectManagerController("projects.json")
        self._selected_date: Optional[dt.date] = None

        # layout
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # top bar with "+ Add New Task" (pill)
        top = ctk.CTkFrame(self, fg_color="transparent")
        top.grid(row=0, column=0, sticky="ew", padx=10, pady=(10, 6))
        ctk.CTkLabel(
            top,
            text=dt.datetime.now().strftime("Today is : %d %B %Y %H:%M:%S"),
            font=("Inter", 12, "bold"),
        ).pack(anchor="w")
        row = ctk.CTkFrame(top, fg_color="transparent")
        row.pack(fill="x", pady=(4, 0))
        ctk.CTkLabel(
            row, text="Task", font=FONT_HEADER, text_color=TITLE_TEXT_COLOR
        ).pack(side="left")
        right_cta = ctk.CTkFrame(row, fg_color="transparent")
        right_cta.pack(side="right")

        ctk.CTkButton(
            right_cta,
            text="+ Add Project",
            height=36,
            corner_radius=18,
            fg_color="#3E3E3E",
            text_color="#FFFFFF",
            hover_color="#555555",
            command=self._open_add_project,
        ).pack(side="right", padx=(0, 16))

        ctk.CTkButton(
            right_cta,
            text="+ Add New Task",
            height=36,
            corner_radius=24,
            fg_color=BUTTON_COLOR,
            text_color=BLACK_COLOR,
            hover_color="#D6D6D6",
            command=self._open_add_task,
        ).pack(side="right", padx=(0, 16))

        # main two columns
        main = ctk.CTkFrame(self, fg_color="transparent")
        main.grid(row=1, column=0, sticky="nsew", padx=10, pady=(6, 8))
        main.grid_columnconfigure(0, weight=3)
        main.grid_columnconfigure(1, weight=2)
        main.grid_rowconfigure(0, weight=1)

        # LEFT: Active Task + Projects
        left = ctk.CTkFrame(main, fg_color="transparent")
        left.grid(row=0, column=0, sticky="nsew", padx=(0, 8))
        left.grid_rowconfigure(0, weight=1)
        left.grid_columnconfigure(0, weight=1)

        self.active_panel = ctk.CTkFrame(left, corner_radius=18, fg_color="#4B4B4B")
        self.active_panel.grid(row=0, column=0, sticky="nsew")
        ctk.CTkLabel(
            self.active_panel, text="Active Task", font=("Inter", 16, "bold")
        ).pack(pady=(10, 6))

        self.task_list = ctk.CTkScrollableFrame(
            self.active_panel, fg_color="#3F3F3F", corner_radius=14
        )
        self.task_list.pack(fill="both", expand=True, padx=10, pady=(4, 10))

        proj_wrap = ctk.CTkFrame(left, fg_color="transparent")
        proj_wrap.grid(row=1, column=0, sticky="ew", pady=(8, 0))
        ctk.CTkLabel(proj_wrap, text="Project", font=("Inter", 14, "bold")).pack(
            anchor="w", padx=4, pady=(0, 6)
        )
        self.proj_cards = ctk.CTkFrame(proj_wrap, fg_color="#4B4B4B", corner_radius=18)
        self.proj_cards.pack(fill="x")

        # RIGHT: Planned + Calendar
        right = ctk.CTkFrame(main, fg_color="transparent")
        right.grid(row=0, column=1, sticky="nsew", padx=(8, 0))
        self._build_planned(right)
        self.calendar = CalendarCard(right, on_select=self._on_date_selected)
        self.calendar.grid(row=1, column=0, sticky="nsew", pady=(8, 0))
        right.grid_rowconfigure(1, weight=1)

        # context menu (Edit/Delete/Timer)
        self.menu = tk.Menu(self, tearoff=False)
        self.menu.add_command(
            label="Edit", command=self._menu_edit, font=("Inter", 10, "bold")
        )
        self.menu.add_command(
            label="Delete", command=self._menu_delete, font=("Inter", 10, "bold")
        )
        self.menu.add_command(
            label="Timer", command=self._open_timer_window, font=("Inter", 10, "bold")
        )
        self._menu_task: Optional[Task] = None

        self._reload_and_render()

    def _open_timer_window(self):
        """Open timer window for the selected task"""
        if not hasattr(self, "timer_window"):
            self.timer_window = None

        if self.timer_window is None or not self.timer_window.winfo_exists():
            self.timer_window = ctk.CTkToplevel(self)
            task_title = self._menu_task.title if self._menu_task else "Timer"
            self.timer_window.title(f"Timer - {task_title}")
            self.timer_window.geometry("350x550")
            self.timer_window.resizable(False, False)
            self.timer_window.attributes("-topmost", True)

            # Create timer frame with padding
            timer_frame = TimerPage(self.timer_window)
            timer_frame.pack(fill="both", expand=True, padx=20, pady=20)

            # Handle window close event
            self.timer_window.protocol("WM_DELETE_WINDOW", self._on_timer_window_close)
        else:
            # If window already exists, just focus it
            self.timer_window.focus_set()
            self.timer_window.lift()

    def _on_timer_window_close(self):
        """Handle timer window closing"""
        if self.timer_window:
            # Find and shutdown any timer instances
            for child in self.timer_window.winfo_children():
                if isinstance(child, TimerPage):
                    try:
                        child._shutdown_timer()
                    except AttributeError:
                        # If _shutdown_timer doesn't exist, just pass
                        pass
                    break
            self.timer_window.destroy()
            self.timer_window = None

    # ---------- top actions ----------
    def _open_add_task(self):
        names = [p.name for p in self.pm.list_projects()]
        AddTaskDialog(
            self,
            on_done=self._add_task,
            project_names=names,
            preset_date=self._selected_date,
        )

    def _add_task(self, payload: dict):
        if not payload.get("title"):
            return
        self.tm.add_task(**payload)
        self._reload_and_render()

    # ---------- project edit handlers ----------
    def _open_edit_project_by_name(self, name: str):
        proj = next((p for p in self.pm.list_projects() if p.name == name), None)
        if not proj:
            return
        EditProjectDialog(self, proj, on_save=self._save_project_edit)

    def _save_project_edit(
        self, proj: Project, new_name: str, new_color: Optional[str]
    ):
        if new_name is None:
            # Remove project
            self.pm.delete_project(proj.id)
            # Clear project from tasks
            tasks = self.tm.view_tasks()
            for t in tasks:
                if t.project == proj.name:
                    self.tm.update_task(t.id, project=None)
        else:
            old_name = proj.name
            self.pm.update_project(proj.id, name=new_name, color=new_color)
            tasks = self.tm.view_tasks()
            for t in tasks:
                if t.project == old_name:
                    self.tm.update_task(t.id, project=new_name)

        self._reload_and_render()

    def _open_add_project(self):
        AddProjectDialog(self, on_done=self._add_project)

    def _add_project(self, name: str, color: Optional[str]):
        if not name:
            return
        self.pm.add_project(name, color)
        self._reload_and_render()

    # ---------- context menu ----------
    def _open_context_menu(self, task: Task):
        self._menu_task = task
        try:
            self.menu.tk_popup(self.winfo_pointerx(), self.winfo_pointery())
        finally:
            self.menu.grab_release()

    def _menu_edit(self):
        if not self._menu_task:
            return
        names = [p.name for p in self.pm.list_projects()]
        EditTaskDialog(
            self, self._menu_task, on_done=self._apply_update, project_names=names
        )

    def _apply_update(self, task_id: str, payload: dict):
        self.tm.update_task(task_id, **payload)
        self._reload_and_render()

    def _menu_delete(self):
        if not self._menu_task:
            return
        self.tm.delete_task(self._menu_task.id)
        self._menu_task = None
        self._reload_and_render()

    # ---------- calendar ----------
    def _on_date_selected(self, day: Optional[dt.date]):
        # Enhanced: Handle None to clear filter when date is deselected
        self._selected_date = day
        self._reload_and_render()

    # ---------- planned block ----------
    def _build_planned(self, parent):
        panel = ctk.CTkFrame(parent, corner_radius=18, fg_color="#4B4B4B")
        panel.grid(row=0, column=0, sticky="ew")
        panel.grid_columnconfigure(0, weight=1)
        self.lbl_today_big = ctk.CTkLabel(panel, text="0", font=("Inter", 54, "bold"))
        self.lbl_today_big.grid(row=0, column=0, sticky="w", padx=14, pady=6)
        block = ctk.CTkFrame(panel, fg_color="transparent")
        block.grid(row=0, column=1, sticky="e", padx=14, pady=12)
        ctk.CTkLabel(block, text="Planned\nToday", font=("Inter", 16, "bold")).pack(
            anchor="e"
        )
        self.l_over = ctk.CTkLabel(block, text="Overdue  0", font=("Inter", 13))
        self.l_over.pack(anchor="w")
        self.l_today = ctk.CTkLabel(block, text="Due Today  0", font=("Inter", 13))
        self.l_today.pack(anchor="w")
        self.l_week = ctk.CTkLabel(block, text="Due This Week  0", font=("Inter", 13))
        self.l_week.pack(anchor="w")

    # ---------- render ----------
    def _reload_and_render(self):
        # clear list & cards
        for w in self.task_list.winfo_children():
            w.destroy()
        for w in self.proj_cards.winfo_children():
            w.destroy()

        # projects lookup by name
        projects = self.pm.list_projects()
        proj_by_name: dict[str, Project] = {p.name: p for p in projects}

        # tasks (optionally filtered by selected date)
        tasks = self.tm.view_tasks()

        # group like mock
        today = self._selected_date if self._selected_date else dt.date.today()
        start_week = today - dt.timedelta(days=today.weekday())
        end_week = start_week + dt.timedelta(days=6)
        last7_start = today - dt.timedelta(days=7)
        last7_end = today - dt.timedelta(days=1)

        groups = {
            "Last 7 days": [],
            "Today": [],
            "This Week": [],
            "Completed": [],  # completed (today)
        }

        for t in tasks:
            if t.status == "done":
                if t.due_date:
                    try:
                        d = dt.datetime.strptime(t.due_date, DATE_FMT).date()
                        if d == today:
                            groups["Completed"].append(t)
                    except ValueError:
                        pass
                continue

            due = None
            if t.due_date:
                try:
                    due = dt.datetime.strptime(t.due_date, DATE_FMT).date()
                except ValueError:
                    pass

            if due and last7_start <= due <= last7_end:
                groups["Last 7 days"].append(t)
            elif due == today:
                groups["Today"].append(t)
            elif due and start_week <= due <= end_week:
                groups["This Week"].append(t)

        # section builder
        def section(title, items):
            row = ctk.CTkFrame(self.task_list, fg_color="transparent")
            ctk.CTkLabel(row, text=f"{title}", font=("Inter", 14, "bold")).pack(
                side="left"
            )
            ctk.CTkLabel(
                row, text=str(len(items)), font=("Inter", 12), text_color="#9A9A9A"
            ).pack(side="left", padx=(6, 0))
            row.pack(fill="x", pady=(12, 8))

            for t in items:
                TaskItem(
                    self.task_list,
                    t,
                    proj_by_name,
                    on_toggle=self._toggle_status,
                    on_open_menu=self._open_context_menu,
                    on_edit_project=self._open_edit_project_by_name,
                ).pack(fill="x", padx=10, pady=6)

        for key in ["Last 7 days", "Today", "This Week", "Completed"]:
            section(key, groups[key])

        # planned numbers (use all tasks, not filtered)
        self._update_planned(self.tm.view_tasks())

        # project cards (click to edit)
        per_row = 3
        for i, p in enumerate(projects):
            bg = _hex(p.color) or (
                "#F7B4BB" if i % 3 == 0 else "#FFF9B3" if i % 3 == 1 else "#BFF4C8"
            )
            card = ctk.CTkFrame(self.proj_cards, corner_radius=18, fg_color=bg)
            ctk.CTkLabel(
                card, text=p.name, font=("Inter", 13, "bold"), text_color=BLACK_COLOR
            ).pack(pady=(12, 0))
            remaining = sum(
                1
                for t in self.tm.view_tasks()
                if t.project == p.name and t.status != "done"
            )
            ctk.CTkLabel(
                card,
                text=str(remaining),
                font=("Inter", 42, "bold"),
                text_color=BLACK_COLOR,
            ).pack(pady=(4, 4))
            ctk.CTkLabel(
                card, text="Task Remaining", font=("Inter", 11), text_color=BLACK_COLOR
            ).pack(pady=(0, 14))
            # click to edit
            card.bind(
                "<Button-1>",
                lambda e, name=p.name: self._open_edit_project_by_name(name),
            )
            for ch in card.winfo_children():
                ch.bind(
                    "<Button-1>",
                    lambda e, name=p.name: self._open_edit_project_by_name(name),
                )
            r, c = divmod(i, per_row)
            card.grid(row=r, column=c, padx=14, pady=14, sticky="nsew")
            self.proj_cards.grid_columnconfigure(c, weight=1)

    def _toggle_status(self, task_id: str, new_status: str):
        self.tm.update_task(task_id, status=new_status)
        self._reload_and_render()

    def _update_planned(self, tasks: list[Task]):
        today = dt.date.today()
        start_week = today - dt.timedelta(days=today.weekday())
        end_week = start_week + dt.timedelta(days=6)
        overdue = due_today = due_week = 0
        for t in tasks:
            if t.status == "done" or not t.due_date:
                continue
            try:
                d = dt.datetime.strptime(t.due_date, DATE_FMT).date()
            except ValueError:
                continue
            if d < today:
                overdue += 1
            elif d == today:
                due_today += 1
            elif start_week <= d <= end_week:
                due_week += 1
        self.lbl_today_big.configure(text=str(due_today))
        self.l_over.configure(text=f"Overdue  {overdue}")
        self.l_today.configure(text=f"Due Today  {due_today}")
        self.l_week.configure(text=f"Due This Week  {due_week}")
