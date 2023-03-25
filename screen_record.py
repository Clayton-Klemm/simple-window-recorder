import tkinter as tk
import threading
import cv2
import numpy as np
import pyautogui
import datetime

class ScreenRecorder:
    def __init__(self):
        self.recording = False
        self.stop_event = threading.Event()

    def start_recording(self, window_title):
        self.recording = True
        self.stop_event.clear()
        threading.Thread(target=self._record_screen, args=(window_title,)).start()

    def stop_recording(self):
        self.recording = False
        self.stop_event.set()

    def _record_screen(self, window_title):
        window_pos = pyautogui.getWindowsWithTitle(window_title)[0]
        if window_pos is None:
            print("Window not found")
            return
        if window_pos.isMinimized:
            window_pos.restore()
        top_left_x, top_left_y, width, height = window_pos.topleft[0], window_pos.topleft[1], window_pos.width, window_pos.height
        screen_size = (width, height)
        fourcc = cv2.VideoWriter_fourcc(*"XVID")        
        # Grab the current time and format it as a string
        current_time = datetime.datetime.now()
        time_str = current_time.strftime("%H-%M-%S")
        
        # Append the current time to the video file name
        time_str_video_name = time_str + ".avi"
        
        # Pass the current time string into the VideoWriter object
        out = cv2.VideoWriter(time_str_video_name, fourcc, 20.0, screen_size)
        
        while self.recording:
            if self.stop_event.is_set():
                break
            img = pyautogui.screenshot(region=(top_left_x, top_left_y, width, height))
            frame = np.array(img)
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            out.write(frame)
        out.release()

class App:
    def __init__(self, master):
        self.master = master
        self.master.geometry("350x400")
        self.master.title("Screen Recorder")
        self.recorder = ScreenRecorder()

        self.label = tk.Label(master, text="Enter window title")
        self.label.pack(fill=tk.NONE, expand=False, side=tk.TOP, padx=10, pady=10)

        self.window_title_entry = tk.Entry(master)
        self.window_title_entry.pack(fill=tk.NONE, expand=False, side=tk.TOP, padx=10, pady=5)

        self.start_button = tk.Button(master, text="Start Recording", command=self.start_recording)
        self.stop_button = tk.Button(master, text="Stop Recording", command=self.stop_recording, state=tk.DISABLED)
        self.start_button.pack(fill=tk.BOTH, expand=True, side=tk.TOP, padx=10, pady=5)
        self.stop_button.pack(fill=tk.BOTH, expand=True, side=tk.TOP, padx=10, pady=5)

    def start_recording(self):
        window_title = self.window_title_entry.get()
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.recorder.start_recording(window_title)

    def stop_recording(self):
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.recorder.stop_recording()

if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()