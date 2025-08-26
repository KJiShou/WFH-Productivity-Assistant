import tkinter.messagebox as msgbox
from typing import Optional

import customtkinter as ctk

from app.controllers.project_manager_controller import Project
from app.views.components.date_picker import _hex


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
        ).pack(side="right", padx=(0, 16))


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
        if msgbox.askyesno(
            "Delete Project",
            f"Are you sure you want to delete '{self.proj.name}'?\n\nThis action cannot be undone.",
        ):
            self.on_save(self.proj, None, None)
            self.destroy()
