import datetime as dt
from tkinter import messagebox
from typing import Optional

import customtkinter as ctk

from app.controllers.task_manager_controller import Task
from app.views.components.date_picker import DatePicker


# Base dialog class with common task form fields
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
        self.dp_due = DatePicker(self)
        self.dp_due.grid(row=3, column=1, padx=10, pady=8, sticky="ew")

        ctk.CTkLabel(self, text="Status").grid(
            row=4, column=0, padx=10, pady=8, sticky="w"
        )
        self.c_status = ctk.CTkOptionMenu(self, values=["todo", "doing", "done"])
        self.c_status.grid(row=4, column=1, padx=10, pady=8, sticky="w")

        bar = ctk.CTkFrame(self, fg_color="transparent")
        bar.grid(row=5, column=0, columnspan=2, sticky="e", padx=10, pady=14)

        ctk.CTkButton(bar, text="Cancel", command=self.destroy).pack(side="right")
        self.ok_btn = ctk.CTkButton(bar, text="Save", command=self._save)
        self.ok_btn.pack(side="right", padx=(0, 16))

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
            due_date=self.dp_due.get_date_str(),
            status=self.c_status.get(),
        )

    def _save(self):
        pass


# Dialog for creating new tasks
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
        if not payload.get("title") or not payload.get("date"):
            messagebox.showerror(
                "Failed", f"There must be title and due date to add task"
            )
            return
        self.on_done(payload)
        self.destroy()


# Dialog for editing existing tasks
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
        if self._values().get("title") == "" or not self._values().get("title"):
            messagebox.showerror("Failed", f"There must be title to save task")
            return
        self.on_done(self.task.id, self._values())
        self.destroy()
