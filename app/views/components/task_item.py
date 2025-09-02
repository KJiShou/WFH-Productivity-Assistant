import customtkinter as ctk

from app.controllers.task_manager_controller import Task
from app.controllers.project_manager_controller import Project
from app.utils.theme import WHITE_COLOR, SELECT_BOX_COLOR
from app.views.components.date_picker import _hex, _pill


# Individual task display widget with checkbox, title, and project pill
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
        elif self.task.status == "doing":
            self.toggle.configure(fg_color="#5288f1", text="-")
        else:
            self.toggle.configure(fg_color="#2B2B2B", text="")

    def _toggle_click(self):
        new_status = "done" if self.task.status != "done" else "todo"
        self.task.status = new_status
        self._style_toggle()
        self.on_toggle(self.task.id, new_status)
