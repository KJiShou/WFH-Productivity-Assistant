import tkinter as tk
import customtkinter as ctk
import time
from PIL import Image

TIMER_TOP_MIDDLE_COLOR = "#565656"
TIMER_MIDDLE_MIDDLE_COLOR = "#969696"
TIMER_BOTTOM_MIDDLE_COLOR = "#D9D9D9"
TIMER_HOVER_COLOR = "#FFFFFF"  # transparency 50%

class TimerPage(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color="transparent")

        # === Header ===
        ctk.CTkLabel(self, text="Timer", font=("Times New Roman", 18), text_color=TIMER_HOVER_COLOR).pack(anchor="w", padx=10, pady=10)

        # === Real Time Display ===
        self.timeNow = ctk.CTkLabel(self, text="", text_color=TIMER_HOVER_COLOR)
        self.timeNow.pack(pady=20)
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

        # === Control Buttons ===
        startImg = ctk.CTkImage(
            Image.open("app/assets/StartIcon.png"),
            size=(20, 20),
        )
        stopImg = ctk.CTkImage(
            Image.open("app/assets/StopIcon.png"),
            size=(20, 20),
        )
        resetImg = ctk.CTkImage(
            Image.open("app/assets/ResetIcon.png"),
            size=(20, 20),
        )

        self.buttonFrame = ctk.CTkFrame(self)
        self.buttonFrame.pack(pady=10)

        self.startButton = ctk.CTkButton(self.buttonFrame, text="Start", image = startImg, command=self.startTimer)
        self.stopButton = ctk.CTkButton(self.buttonFrame, text="Stop", image = stopImg, command=self.stopTimer)
        self.startButton.pack(pady=0)

        self.resetButton = ctk.CTkButton(self, text="Reset", image = resetImg, command=self.resetTimer)
        self.resetButton.pack(pady=10)

        # Timer state
        self.run_timer = False
        self.remaining_second = 0
        self.totalTime = 0

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
            font=("Times New Roman", 17)
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

            if event.delta > 0:   # scroll up
                if current > 0:
                    new_index = current - 1
                    listBox.selection_clear(0, tk.END)
                    listBox.selection_set(new_index)
                    listBox.see(new_index)
            else:   # scroll down
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
        listBox.bind("<Button-4>", lambda e: on_mouse_wheel(type("Event", (), {"delta": 120})))
        listBox.bind("<Button-5>", lambda e: on_mouse_wheel(type("Event", (), {"delta": -120})))

    def hideScrollBar(self):
        for widget in self.scrollFrame.winfo_children():
            widget.grid_remove()

    def showScrollBar(self):
        for widget in self.scrollFrame.winfo_children():
            widget.grid()

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
            minutes = int((self.remaining_second // 60) % 60)

            self.timeSet.configure(text=f"{minutes:02d} : {seconds:02d}")

            # Progress Bar
            progress = (self.remaining_second / self.totalTime) % 100
            self.progressBar.set(progress)

            self.remaining_second -= 1
            self.timeSet.after(1000, self.updateTimer)
        elif self.remaining_second == 0:
            self.timeSet.configure(text="00 : 00")
            self.progressBar.set(100)
            self.run_timer = False

    def startTimer(self):
        if self.run_timer:
            return

        if self.remaining_second == 0:
            self.remaining_second = self.totalSec()
            self.totalTime = self.remaining_second

        if self.remaining_second == 0 or self.remaining_second >= 3600:
            return

        self.run_timer = True
        self.hideScrollBar()
        self.startButton.pack_forget()
        self.stopButton.pack()
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

        self.minutesBox.selection_clear(0, "end")
        self.minutesBox.selection_set(0)
        self.minutesBox.see(0)

        self.secondsBox.selection_clear(0, "end")
        self.secondsBox.selection_set(0)
        self.secondsBox.see(0)

        self.remaining_second = 0
        self.progressBar.set(100)
        self.run_timer = False