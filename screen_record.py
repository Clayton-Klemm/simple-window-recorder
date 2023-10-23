# Import the necessary libraries:
# tkinter for creating a graphical user interface (GUI), threading for executing 
# tasks in parallel (so the main application doesn't freeze during recording), 
# cv2 for capturing and saving video, numpy for array operations, pyautogui for 
# screen capture and GUI interactions, and datetime for time-based filename generation
# to prevent recording overwritting. 
import tkinter as tk
import threading
import cv2
import numpy as np
import pyautogui
from datetime import datetime

class ScreenRecorder:
    def __init__(self):
        # Initialization: set the recording status to False by default. 
        # The threading.Event allows communication between threads to stop the recording.
        self.recording = False
        self.stop_event = threading.Event()

    def start_recording(self, window_title):
        # Begin recording. Set the recording status and clear any stop signals. 
        # A new thread is started to perform the recording to avoid freezing the main application.
        self.recording = True
        self.stop_event.clear()
        threading.Thread(target=self._record_screen, args=(window_title,)).start()

    def stop_recording(self):
        # Stop the recording by updating the recording status and setting the stop signal.
        self.recording = False
        self.stop_event.set()

    def _record_screen(self, window_title):
        windows = pyautogui.getWindowsWithTitle(window_title)
        # Check if the list 'windows' is empty. If it is, inform the user and return.
        if not windows:
            print("Window not found")
            return
        
        # If the list is not empty, proceed with the first window.
        window_pos = windows[0]
        
        # If the targeted window is minimized, restore it to capture its contents.
        if window_pos.isMinimized:
            window_pos.restore()

        # Define the recording area size based on the target window's size.
        screen_size = (window_pos.width, window_pos.height)
        # Set up a video writer to save the captured frames with the desired format and size.
        out = cv2.VideoWriter(self._generate_filename(), cv2.VideoWriter_fourcc(*"XVID"), 20.0, screen_size)

        # Continuously capture the screen as long as recording is desired.
        while self.recording:
            # If a stop signal is received, end the loop and stop recording.
            if self.stop_event.is_set():
                break

            # Capture a screenshot of the targeted window area and convert it to a format suitable for video storage.
            frame = np.array(pyautogui.screenshot(region=(window_pos.topleft[0], window_pos.topleft[1], *screen_size)))
            out.write(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        
        # Close the video writer to finalize the video file.
        out.release()

    def _generate_filename(self):
        # Generate a unique filename based on the current time to avoid overwriting previous recordings.
        return datetime.now().strftime("%H-%M-%S") + ".avi"

class App:
    def __init__(self, master):
        # Set up the main application window and initialize the screen recorder.
        self.master = master
        self.recorder = ScreenRecorder()

        # Build the visual components of the application.
        self._setup_ui()

    def _setup_ui(self):
        # Define the size and title of the main application window.
        self.master.geometry("350x400")
        self.master.title("Screen Recorder")

        # Create visual elements: a label, an input field, and control buttons.
        self._create_label()
        self._create_entry()
        self._create_buttons()

    def _create_label(self):
        # Display instructions for the user.
        tk.Label(self.master, text="Enter window title").pack(padx=10, pady=10)

    def _create_entry(self):
        # Create an input field where the user can type the name of the window they want to record.
        self.window_title_entry = tk.Entry(self.master)
        self.window_title_entry.pack(padx=10, pady=5)

    def _create_buttons(self):
        # Create buttons allowing the user to start and stop the recording. 
        # Initially, the stop button is disabled since there's no ongoing recording.
        self.start_button = tk.Button(self.master, text="Start Recording", command=self.start_recording)
        self.stop_button = tk.Button(self.master, text="Stop Recording", command=self.stop_recording, state=tk.DISABLED)

        self.start_button.pack(fill=tk.BOTH, padx=10, pady=5)
        self.stop_button.pack(fill=tk.BOTH, padx=10, pady=5)

    def start_recording(self):
        # When recording starts, disable the start button to prevent multiple recordings 
        # and enable the stop button so the user can end the recording.
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.recorder.start_recording(self.window_title_entry.get())

    def stop_recording(self):
        # When recording stops, revert the button states to their initial configuration.
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.recorder.stop_recording()

# If this script is run directly (not imported), initiate the GUI application.
if __name__ == "__main__":
    root = tk.Tk()  # Start the main GUI window.
    app = App(root)  # Initialize our application using the main window.
    root.mainloop()  # Enter the main event loop, allowing user interactions.
