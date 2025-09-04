import tkinter as tk
import customtkinter as ctk
import time
from PIL import Image
import winsound
import json
import os
import tkinter.messagebox as messagebox
from datetime import datetime
from app.controllers.timer_controller import TimerController

STORAGE_PATH = "timer_record.json"

TIMER_TOP_MIDDLE_COLOR = "#565656"
TIMER_MIDDLE_MIDDLE_COLOR = "#969696"
TIMER_BOTTOM_MIDDLE_COLOR = "#D9D9D9"
TIMER_HOVER_COLOR = "#FFFFFF"  # transparency 50%


def save_record(task_id, start_day, start_datetime, duration_seconds):
    timer_controller = TimerController(STORAGE_PATH)
    start_day_str = start_day.strftime("%A")
    start_datetime_str = start_datetime.strftime("%d/%m/%Y %H:%M:%S")
    duration_str = f"{duration_seconds // 60:02d}:{duration_seconds % 60:02d}"
    timer_controller.add_record(
        task_id, start_day_str, start_datetime_str, duration_str
    )


class TimerPage(ctk.CTkFrame):
    def __init__(self, parent, task_id: str, task_name: str):
        super().__init__(parent, fg_color="transparent")

        # === Header ===
        # === Task ID and Name ===
        self.task_id = task_id
        self.task_name = task_name

        self.title_label = ctk.CTkLabel(
            self,
            text=f"Timer for: {self.task_name}",
            font=("Arial", 16, "bold", "underline"),
        )
        self.title_label.pack(pady=10)

        # === Real Time Display ===
        self.timeNow = ctk.CTkLabel(self, text="", text_color=TIMER_HOVER_COLOR)
        self.timeNow.pack(pady=10)
        self.currentTime()

        # === Countdown Label ===
        self.timeSet = ctk.CTkLabel(self, text="00 : 00", font=("Times New Roman", 20))
        self.timeSet.pack(pady=10)

        # === Progress Bar ===
        self.progressBar = ctk.CTkProgressBar(self, width=200, height=5)
        self.progressBar.pack(pady=10)
        self.progressBar.set(100)

        # === Scroll Pickers ===
        self.scrollFrame = ctk.CTkFrame(self, fg_color="transparent")
        self.scrollFrame.pack(pady=10)

        self.minutesBox = self.picker(self.scrollFrame, 60, 0, default_value=0)
        self.secondsBox = self.picker(self.scrollFrame, 60, 1, default_value=0)

        self.bindOneStepScroll(self.minutesBox)
        self.bindOneStepScroll(self.secondsBox)

        self.minutesBox.bind("<<ListboxSelect>>", self.totalSec)
        self.secondsBox.bind("<<ListboxSelect>>", self.totalSec)

        # === Preset Time Button ===
        self.presetFrame = ctk.CTkFrame(self, fg_color="transparent")
        self.presetFrame.pack(pady=10)

        button_style = {
            "width": 50,
            "height": 50,
            "corner_radius": 30,  # half of width/height → circle
            "fg_color": "#555555",  # gray background
            "text_color": "white",  # white text
            "font": ("Times New Roman", 14, "bold"),
        }

        self.button1 = ctk.CTkButton(
            self.presetFrame,
            text="15:00",
            command=lambda: self.setTime(15, 0),
            **button_style,
        )
        self.button2 = ctk.CTkButton(
            self.presetFrame,
            text="30:00",
            command=lambda: self.setTime(30, 0),
            **button_style,
        )
        self.button3 = ctk.CTkButton(
            self.presetFrame,
            text="60:00",
            command=lambda: self.setTime(60, 0),
            **button_style,
        )

        self.button1.grid(row=0, column=0, padx=10)
        self.button2.grid(row=0, column=1, padx=10)
        self.button3.grid(row=0, column=2, padx=10)

        # === Control Buttons ===
        self.buttonFrame = ctk.CTkFrame(self)
        self.buttonFrame.pack(pady=10)

        startImg = ctk.CTkImage(Image.open("app/assets/StartIcon.png"), size=(20, 20))
        stopImg = ctk.CTkImage(Image.open("app/assets/StopIcon.png"), size=(20, 20))
        resetImg = ctk.CTkImage(Image.open("app/assets/ResetIcon.png"), size=(20, 20))
        endImg = ctk.CTkImage(Image.open("app/assets/EndIcon.png"), size=(20, 20))

        self.startButton = ctk.CTkButton(
            self.buttonFrame, text="Start", image=startImg, command=self.startTimer
        )
        self.stopButton = ctk.CTkButton(
            self.buttonFrame, text="Stop", image=stopImg, command=self.stopTimer
        )
        self.startButton.pack(pady=0)

        self.resetButton = ctk.CTkButton(
            self, text="Reset", image=resetImg, command=self.resetTimer
        )
        self.resetButton.pack(pady=0)

        self.endButton = ctk.CTkButton(
            self, text="  End", image=endImg, command=self.endTimer
        )
        self.endButton.pack(pady=10)

        # Timer state
        self.run_timer = False
        self.remaining_second = 0
        self.totalTime = 0

    def showImagePopup(self):
        popup = ctk.CTkToplevel(self)
        popup.attributes("-topmost", True)
        popup.geometry("400x600")
        popup.grab_set()  # make modal

        # Load image
        img = ctk.CTkImage(Image.open("app/assets/timesup.jpg"), size=(350, 500))

        label = ctk.CTkLabel(popup, image=img, text="")
        label.pack(pady=20)
        label.image = img  # prevent garbage collection

        ctk.CTkButton(popup, text="OK", command=popup.destroy).pack(pady=10)

    # === Real Time Clock ===
    def currentTime(self):
        hour = time.strftime("%I")
        minute = time.strftime("%M")
        second = time.strftime("%S")
        day = time.strftime("%A")
        date = time.strftime("%d")
        month = time.strftime("%B")
        year = time.strftime("%Y")

        self.timeNow.configure(
            text=f"Today is: {day} {date} {month} {year} {hour}:{minute}:{second}"
        )
        self.timeNow.after(1000, self.currentTime)

    # === Picker (Minutes/Seconds) ===
    def picker(self, master, count, col, default_value=0):
        frame = ctk.CTkFrame(master, fg_color="transparent")
        frame.grid(row=0, column=col, padx=10)

        listBox = tk.Listbox(
            frame,
            height=5,
            exportselection=False,
            justify="center",
            width=4,
            bg="#2b2b2b",
            fg="white",
            highlightthickness=0,
            selectbackground="#444444",
            font=("Times New Roman", 17),
        )
        listBox.pack()

        for i in range(count):
            listBox.insert(tk.END, f"{i:02d}")

        for i in range(listBox.size()):
            if listBox.get(i) == f"{default_value:02d}":
                listBox.select_set(i)
                listBox.see(max(0, i - 2))
                break

        return listBox

    def bindOneStepScroll(self, listBox):
        def on_mouse_wheel(event):
            if not listBox.curselection():
                return "break"
            current = listBox.curselection()[0]

            if event.delta > 0:  # scroll up
                if current > 0:
                    new_index = current - 1
                    listBox.selection_clear(0, tk.END)
                    listBox.selection_set(new_index)
                    listBox.see(new_index)
            else:  # scroll down
                if current < listBox.size() - 1:
                    new_index = current + 1
                    listBox.selection_clear(0, tk.END)
                    listBox.selection_set(new_index)
                    listBox.see(new_index)

            # update timer label directly
            try:
                minute = int(self.minutesBox.get(self.minutesBox.curselection()))
                second = int(self.secondsBox.get(self.secondsBox.curselection()))
                self.timeSet.configure(text=f"{minute:02d} : {second:02d}")
            except:
                pass

            return "break"

        listBox.bind("<MouseWheel>", on_mouse_wheel)
        listBox.bind(
            "<Button-4>", lambda e: on_mouse_wheel(type("Event", (), {"delta": 120}))
        )
        listBox.bind(
            "<Button-5>", lambda e: on_mouse_wheel(type("Event", (), {"delta": -120}))
        )

    def hideScrollBar(self):
        for widget in self.scrollFrame.winfo_children():
            widget.grid_remove()

    def showScrollBar(self):
        for widget in self.scrollFrame.winfo_children():
            widget.grid()

    def setTime(self, minute, second):
        self.timeSet.configure(text=f"{minute:02d} : {second:02d}")
        self.remaining_second = minute * 60 + second
        self.totalTime = self.remaining_second

    def totalSec(self, event=None):
        try:
            minute = int(self.minutesBox.get(self.minutesBox.curselection()))
            second = int(self.secondsBox.get(self.secondsBox.curselection()))
            self.timeSet.configure(text=f"{minute:02d} : {second:02d}")
            return minute * 60 + second
        except:
            return 0

    def updateTimer(self):
        if self.run_timer and self.remaining_second > 0:
            seconds = int(self.remaining_second % 60)
            minutes = int(self.remaining_second // 60)

            self.timeSet.configure(text=f"{minutes:02d} : {seconds:02d}")

            # Progress Bar
            progress = (self.remaining_second / self.totalTime) % 100
            self.progressBar.set(progress)

            self.remaining_second -= 1
            self.timeSet.after(1000, self.updateTimer)

        elif self.remaining_second == 0 and self.run_timer:
            self.run_timer = False
            self.timeSet.configure(text="00 : 00")
            self.progressBar.set(100)

            self.showScrollBar()
            self.stopButton.pack_forget()
            self.startButton.pack()

            self.button1.grid()
            self.button2.grid()
            self.button3.grid()

            self.minutesBox.selection_clear(0, "end")
            self.minutesBox.selection_set(0)
            self.minutesBox.see(0)

            self.secondsBox.selection_clear(0, "end")
            self.secondsBox.selection_set(0)
            self.secondsBox.see(0)

            winsound.PlaySound(
                "app/assets/alarm.wav", winsound.SND_FILENAME | winsound.SND_ASYNC
            )
            self.showImagePopup()
            # messagebox.showinfo("Time's Up!", "The countdown is over.")

            save_record(
                self.task_id,
                self.start_day,
                self.start_datetime,
                self.start_total_seconds,
            )

    def startTimer(self):
        if self.run_timer:
            return

        # Set the start details only the first run
        if self.remaining_second == 0:
            try:
                minute, second = map(int, self.timeSet.cget("text").split(" : "))
                self.remaining_second = minute * 60 + second
                self.totalTime = self.remaining_second
            except:
                return

            self.start_day = datetime.now()
            self.start_datetime = datetime.now()
            self.start_total_seconds = self.totalTime

        self.run_timer = True
        self.hideScrollBar()

        # Hide start button and show stop button
        self.startButton.pack_forget()
        self.stopButton.pack()

        # Hide preset time button
        self.button1.grid_remove()
        self.button2.grid_remove()
        self.button3.grid_remove()

        self.updateTimer()

    def stopTimer(self):
        self.run_timer = False
        self.stopButton.pack_forget()
        self.startButton.pack()

    def resetTimer(self):
        self.timeSet.configure(text="00 : 00")

        self.showScrollBar()
        self.stopButton.pack_forget()
        self.startButton.pack()

        self.button1.grid()
        self.button2.grid()
        self.button3.grid()

        self.minutesBox.selection_clear(0, "end")
        self.minutesBox.selection_set(0)
        self.minutesBox.see(0)

        self.secondsBox.selection_clear(0, "end")
        self.secondsBox.selection_set(0)
        self.secondsBox.see(0)

        self.remaining_second = 0
        self.totalTime = 0
        self.progressBar.set(100)
        self.run_timer = False

    def endTimer(self):
        if not self.start_datetime:  # no active session
            messagebox.showwarning("No Active Task", "No task is currently running.")
            return

        # Pause the timer while asking
        was_running = self.run_timer
        self.run_timer = False

        confirm = messagebox.askyesno(
            "Confirm End Time", "Are you sure you want to end the timer?"
        )
        if confirm:
            used_seconds = self.start_total_seconds - self.remaining_second
            save_record(self.task_id, self.start_day, self.start_datetime, used_seconds)

            # Reset stored values
            self.start_day = None
            self.start_datetime = None
            self.start_total_seconds = None

            self.resetTimer()
            messagebox.showinfo("Task Ended", f"Task {self.task_name} has ended.")
        else:
            # Resume if it was running
            self.run_timer = was_running
            if was_running:
                self.updateTimer()


# === Run Test App ===
if __name__ == "__main__":
    ctk.set_appearance_mode("dark")
    window = ctk.CTk()
    window.title("Timer")
    window.geometry("500x500")

    page = TimerPage(window)
    page.pack(fill="both", expand=True)

    window.mainloop()
