import datetime as dt
import tkinter as tk
from tkinter import messagebox
from typing import Optional

import customtkinter as ctk

from app.utils.theme import (
    FONT_HEADER,
    TITLE_TEXT_COLOR,
    WHITE_COLOR,
    BLACK_COLOR,
    BUTTON_COLOR,
)
from app.controllers.task_manager_controller import (
    TaskManagerController,
    Task,
    DATE_FMT,
)
from app.controllers.project_manager_controller import ProjectManagerController, Project
from app.views.TimerRecord import TimerRecordPage
from app.views.pomodoro_timer import TimerPage
from app.views.components.date_picker import _hex
from app.views.components.task_dialogs import AddTaskDialog, EditTaskDialog
from app.views.components.project_dialogs import AddProjectDialog, EditProjectDialog
from app.views.components.calendar_card import CalendarCard
from app.views.components.task_item import TaskItem


# Main task management page with active tasks, projects, and calendar
class TaskPage(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color="transparent")
        self.tm = TaskManagerController("tasks.json")
        self.pm = ProjectManagerController("projects.json")
        self._selected_date: Optional[dt.date] = None

        # Main page layout configuration
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Header section with date display and action buttons
        top = ctk.CTkFrame(self, fg_color="transparent")
        top.grid(row=0, column=0, sticky="ew", padx=10, pady=(10, 6))
        # === Real Time Display ===
        self.timeNow = ctk.CTkLabel(
            top,
            text="",
            font=("Inter", 13, "bold", "underline"),
        )
        self.timeNow.pack(anchor="w")
        self.currentTime()
        row = ctk.CTkFrame(top, fg_color="transparent")
        row.pack(fill="x", pady=(4, 0))
        ctk.CTkLabel(
            row, text="Task", font=FONT_HEADER, text_color=TITLE_TEXT_COLOR
        ).pack(side="left")
        right_cta = ctk.CTkFrame(row, fg_color="transparent")
        right_cta.pack(side="right")

        ctk.CTkButton(
            right_cta,
            text="Task History",
            height=36,
            corner_radius=18,
            fg_color="#3E3E3E",
            text_color="#FFFFFF",
            hover_color="#555555",
            command=self._open_task_history,
        ).pack(side="right", padx=(0, 16))

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

        # Main content area - two column layout
        main = ctk.CTkFrame(self, fg_color="transparent")
        main.grid(row=1, column=0, sticky="nsew", padx=10, pady=(6, 8))
        main.grid_columnconfigure(0, weight=3)
        main.grid_columnconfigure(1, weight=2)
        main.grid_rowconfigure(0, weight=1)

        # Left column: Active tasks and project cards
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
        self.proj_cards = ctk.CTkScrollableFrame(
            proj_wrap, fg_color="#4B4B4B", corner_radius=18, height=200
        )
        self.proj_cards.pack(fill="x")

        # Right column: Planned tasks summary and calendar widget
        right = ctk.CTkFrame(main, fg_color="transparent")
        right.grid(row=0, column=1, sticky="nsew", padx=(8, 0))
        self._build_planned(right)
        self.calendar = CalendarCard(right, on_select=self._on_date_selected)
        self.calendar.grid(row=1, column=0, sticky="nsew", pady=(8, 0))
        right.grid_rowconfigure(1, weight=1)

        # Right-click context menu for task operations
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

    def currentTime(self):
        """Update the real-time display every second similar to pomodoro timer"""
        hour = dt.datetime.now().strftime("%I")
        minute = dt.datetime.now().strftime("%M")
        second = dt.datetime.now().strftime("%S")
        day = dt.datetime.now().strftime("%A")
        date = dt.datetime.now().strftime("%d")
        month = dt.datetime.now().strftime("%B")
        year = dt.datetime.now().strftime("%Y")

        self.timeNow.configure(
            text=f"Today is: {day} {date} {month} {year} {hour}:{minute}:{second}"
        )
        self.timeNow.after(1000, self.currentTime)

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
            task = self._menu_task
            timer_frame = TimerPage(
                self.timer_window, task_id=task.id, task_name=task_title
            )
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

    # ---------- Task creation handlers ----------
    def _open_add_task(self):
        names = [p.name for p in self.pm.list_projects()]
        AddTaskDialog(
            self,
            on_done=self._add_task,
            project_names=names,
            preset_date=self._selected_date,
        )

    def _add_task(self, payload: dict):
        if not payload.get("title") or not payload.get("due_date"):
            return
        self.tm.add_task(**payload)
        self._reload_and_render()

    # ---------- Project management handlers ----------
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

    # ---------- Task context menu operations ----------
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
        if messagebox.askyesno(
            "Delete Project",
            f"Are you sure you want to delete '{self._menu_task.title}'?\n\nThis action cannot be undone.",
        ):
            self.tm.delete_task(self._menu_task.id)
            self._menu_task = None
            self._reload_and_render()

    # ---------- Task History Section ----------
    def _open_task_history(self):
        # Open a new window to show task history with timer record
        history_win = ctk.CTkToplevel(self)
        history_win.title("Task History")
        history_win.attributes("-topmost", True)
        history_win.geometry("650x500")
        history_win.resizable(True, True)

        history_page = TimerRecordPage(history_win, "timer_record.json")
        history_page.pack(fill="both", expand=True, padx=10, pady=10)

    # ---------- Calendar date selection ----------
    def _on_date_selected(self, day: Optional[dt.date]):
        # Enhanced: Handle None to clear filter when date is deselected
        self._selected_date = day
        self._reload_and_render()

    # ---------- Planned tasks summary widget ----------
    def _build_planned(self, parent):
        panel = ctk.CTkFrame(parent, corner_radius=18, fg_color="#4B4B4B")
        panel.grid(row=0, column=0, sticky="ew")
        panel.grid_columnconfigure(0, weight=1)
        self.lbl_today_big = ctk.CTkLabel(panel, text="0", font=("Inter", 54, "bold"))
        self.lbl_today_big.grid(row=0, column=0, sticky="w", padx=14, pady=6)
        block = ctk.CTkFrame(panel, fg_color="transparent")
        block.grid(row=0, column=1, sticky="e", padx=14, pady=12)
        ctk.CTkLabel(block, text="Planned Today", font=("Inter", 16, "bold")).pack(
            anchor="e"
        )
        self.l_over = ctk.CTkLabel(block, text="Overdue  0", font=("Inter", 13))
        self.l_over.pack(anchor="w")
        self.l_today = ctk.CTkLabel(block, text="Due Today  0", font=("Inter", 13))
        self.l_today.pack(anchor="w")
        self.l_week = ctk.CTkLabel(block, text="Due This Week  0", font=("Inter", 13))
        self.l_week.pack(anchor="w")

    # ---------- Data loading and UI rendering ----------
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
        last_end = today - dt.timedelta(days=1)

        groups = {
            "Overdue": [],
            "Today": [],
            "This Week": [],
            "Completed": [],
        }

        for t in tasks:
            if t.status == "done":
                if t.due_date:
                    try:
                        d = dt.datetime.strptime(t.due_date, DATE_FMT).date()
                        # Include completed tasks from last 7 days and today
                        if d <= today:
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

            if due and due <= last_end:
                groups["Overdue"].append(t)
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

        for key in ["Overdue", "Today", "This Week", "Completed"]:
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
