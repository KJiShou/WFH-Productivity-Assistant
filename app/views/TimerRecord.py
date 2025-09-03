import json
import customtkinter as ctk
import datetime

class TimerRecordPage(ctk.CTkFrame):
    def __init__(self, master, json_file="timer_record.json"):
        super().__init__(master, fg_color="transparent")
        self.json_file = json_file

        ctk.CTkLabel(
            self, text="Timer Record", font=("Inter", 18, "bold")
        ).pack(pady=(10, 6))

        # Scrollable frame
        self.record_list = ctk.CTkScrollableFrame(self, corner_radius=14, fg_color="#3F3F3F")
        self.record_list.pack(fill="both", expand=True, padx=10, pady=10)

        self.load_records()

    # Get the records from JSON File
    def load_records(self):
        # Clear old widgets
        for widget in self.record_list.winfo_children():
            widget.destroy()

        # Load JSON file
        try:
            with open(self.json_file, "r", encoding="utf-8") as file:
                data = json.load(file)
        except (FileNotFoundError, json.JSONDecodeError):
            data = []

        # Group records by (task_id, task_name)
        group = {}
        for rec in data:
            key = (rec.get("task_id"), rec.get("task_name"))
            if key not in group:
                group[key] = []
            group[key].append(rec)

        # Build dropdown for each task group
        for (task_id, task_name), records in group.items():
            self._create_task_dropdown(task_id, task_name, records)

    def _create_task_dropdown(self, task_id, task_name, records):
        # Outer frame for one task
        frame = ctk.CTkFrame(self.record_list, corner_radius=10, fg_color="#4B4B4B")
        frame.pack(fill="x", pady=6)

        total_duration = self.sum_durations(records)

        # Button with record count
        toggle_btn = ctk.CTkButton(
            frame,
            text=f"{task_name} | Records : {len(records)} | Total Time Used : {total_duration}",
            fg_color="#4B4B4B",
            hover_color="#5A5A5A",
            text_color="white",
            anchor="w",
            command=lambda: self._toggle_details(details_frame),
        )
        toggle_btn.pack(fill="x", padx=10, pady=6)

        # Hidden details frame
        details_frame = ctk.CTkFrame(frame, fg_color="#3F3F3F", corner_radius=8)
        details_frame.pack(fill="x", padx=10, pady=(0, 8))
        details_frame.pack_forget()  # hide by default

        # Header row inside dropdown
        header = ctk.CTkFrame(details_frame, fg_color="transparent")
        header.pack(fill="x", pady=(4, 2))
        for i, col in enumerate(["Start Day", "Start Time", "Duration"]):
            ctk.CTkLabel(header, text=col, font=("Inter", 12, "bold"), width=130, anchor="w").grid(row=0, column=i, padx=14)

        # Record rows
        for rec in records:
            row = ctk.CTkFrame(details_frame, fg_color="transparent")
            row.pack(fill="x", padx=6, pady=2)

            ctk.CTkLabel(row, text=rec.get("start_day", ""), width=120, anchor="w").grid(row=0, column=0, padx=6)
            ctk.CTkLabel(row, text=rec.get("start_date_time", ""), width=180, anchor="w").grid(row=0, column=1, padx=6)
            ctk.CTkLabel(row, text=rec.get("duration", ""), width=80, anchor="w").grid(row=0, column=2, padx=6)

    def _toggle_details(self, frame):
        if frame.winfo_ismapped():
            frame.pack_forget()
        else:
            frame.pack(fill="x", padx=10, pady=(0, 8))

    def sum_durations(self, records):
        total_seconds = 0

        for rec in records:
            # Get the duration time for each record, if no duration time then set duration as 00:00
            duration = rec.get("duration", "00:00")
            try:
                # split string into numbers and store into list
                minute, second = map(int, duration.split(":"))
                total_seconds += minute * 60 + second
            except ValueError:
                continue  # skip invalid formats

        # Convert back to HH:MM:SS
        hours, remainder = divmod(total_seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        return f"{hours:02}:{minutes:02}:{seconds:02}"