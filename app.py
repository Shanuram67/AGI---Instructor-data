import threading
import tkinter as tk
from tkinter import messagebox
from queue import Queue
import os
import json
import time 

# === IMPORT CORE MODULES ===
# Import the necessary classes from capture.py (assuming previous files are consolidated)
from capture import ScreenCapturer, AudioCapturer, SCREEN_DIR as CAPTURE_DIR 
from process import Processor, DATA_DIR # Import necessary classes and paths
# Import functions from summarize.py
from summarize import summarize as run_summarize_logic, save_summary, load_events, OUTPUT_SUMMARY as SUMMARY_FILE
# Import the automation function
from automation_runner import run_automation

# ===== GLOBAL PATHS & SETUP =====
# Use the DATA_DIR from the process module for consistency
DATA_DIR = DATA_DIR 
# The file where the Processor outputs its JSONL log (workflows.jsonl)
WORKFLOW_LOG_FILE = os.path.join(DATA_DIR, "processed_events.jsonl") 
# The file where the Summarizer outputs the final JSON summary
FINAL_SUMMARY_JSON = os.path.join(DATA_DIR, "workflow_summaries.json") 
os.makedirs(DATA_DIR, exist_ok=True)


class AGIAssistantApp:
    def __init__(self, root):
        self.root = root
        self.root.title("AGI Assistant Prototype")
        self.root.geometry("400x350")
        self.root.resizable(False, False)
        
        # Communication Queue for the threads
        self.data_queue = Queue() 
        
        # Initialize components (They will run in the background)
        self.capturer = ScreenCapturer(self.data_queue, interval=2.0)
        
        # CORRECTED LINE: Initialize the AudioCapturer component
        self.audio_capturer = AudioCapturer(self.data_queue, duration=3.0) 
        
        self.processor = Processor(self.data_queue, out_file=os.path.basename(WORKFLOW_LOG_FILE))
        
        self.is_recording = False

        # ===== UI Layout =====
        tk.Label(root, text="AGI Assistant Prototype", font=("Arial", 16, "bold")).pack(pady=10)

        self.start_btn = tk.Button(root, text="▶ Start Capture", width=20, command=self.start_capture)
        self.start_btn.pack(pady=5)

        self.stop_btn = tk.Button(root, text="⏹ Stop Capture", width=20, command=self.stop_capture, state=tk.DISABLED)
        self.stop_btn.pack(pady=5)

        # The process button now starts the summarization based on the log file
        self.process_btn = tk.Button(root, text="⚙ Process & Summarize", width=20, command=self.process_data)
        self.process_btn.pack(pady=5)

        self.auto_btn = tk.Button(root, text="🤖 Run Automation", width=20, command=self.trigger_automation, state=tk.DISABLED)
        self.auto_btn.pack(pady=5)

        tk.Button(root, text="🧹 Forget All Data", width=20, command=self.forget_data).pack(pady=20)

        self.status_label = tk.Label(root, text="Status: Idle", fg="blue")
        self.status_label.pack()

    # ===== CAPTURE CONTROL (CORRECTED) =====
    def start_capture(self):
        if self.is_recording:
            return
            
        # Start all three worker threads: Screen, Audio, and Processor
        self.capturer.start_capture()
        self.audio_capturer.start_capture() # <-- New line
        self.processor.start_processing()
        
        self.is_recording = True
        self.start_btn.config(state=tk.DISABLED)
        self.stop_btn.config(state=tk.NORMAL)
        self.auto_btn.config(state=tk.DISABLED)
        self.status_label.config(text="Status: Recording & Processing...", fg="green")

    def stop_capture(self):
        if not self.is_recording:
            return
            
        # Stop all three worker threads
        self.capturer.stop_capture()
        self.audio_capturer.stop_capture() # <-- New line
        self.processor.stop_processing()
        
        # Wait a moment for threads to finish their current work
        time.sleep(1.0) 
        
        self.is_recording = False
        self.start_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)
        self.auto_btn.config(state=tk.NORMAL) # Enable automation after capture stops
        self.status_label.config(text="Status: Capture stopped", fg="red")

    # ===== SUMMARIZATION (POST-PROCESSING) =====
    def process_data(self):
        if self.is_recording:
            messagebox.showwarning("Warning", "Stop capture before processing data.")
            return

        self.status_label.config(text="Status: Summarizing workflow...", fg="orange")
        self.root.update() # Force UI update

        try:
            # 1. Load the raw processed events from the JSONL log file
            events = load_events(WORKFLOW_LOG_FILE)
            
            if not events:
                messagebox.showinfo("Info", "No new events to summarize.")
                self.status_label.config(text="Status: Idle", fg="blue")
                return

            # 2. Run the summarization logic
            summary_list = run_summarize_logic(events)

            # 3. Save the summary to the final JSON file
            save_summary(summary_list, FINAL_SUMMARY_JSON)
            
            self.status_label.config(text=f"Status: Summary ready ({len(summary_list)} types) ✅", fg="green")
            self.auto_btn.config(state=tk.NORMAL)
            messagebox.showinfo("Processing Complete", f"Session summarized successfully! Found {len(summary_list)} unique workflow types.")

        except Exception as e:
            messagebox.showerror("Error", f"An error occurred during summarization: {e}")
            self.status_label.config(text="Status: Error", fg="red")

    # ===== AUTOMATION EXECUTION (UNMODIFIED) =====
    def trigger_automation(self):
        if not os.path.exists(FINAL_SUMMARY_JSON):
            messagebox.showerror("Error", "No summary file found. Please process first.")
            return

        # NOTE: For this demo, we'll manually define a simple automation to run.
        automation_steps = [
            {'action': 'write', 'text': 'Running automation based on detected workflow!', 'delay': 0.5},
            {'action': 'press', 'key': 'enter', 'delay': 0.5},
            {'action': 'move', 'x': 100, 'y': 100, 'delay': 1.0},
        ]
        
        # Run automation in a separate thread to keep the GUI responsive
        threading.Thread(target=lambda: self._execute_automation_in_thread(automation_steps), daemon=True).start()
        
    def _execute_automation_in_thread(self, steps):
        self.status_label.config(text="Status: Automation running 🤖", fg="purple")
        self.auto_btn.config(state=tk.DISABLED)
        
        # Execute the imported function
        run_automation(steps) 
        
        self.status_label.config(text="Status: Automation executed 🤖", fg="blue")
        self.auto_btn.config(state=tk.NORMAL)

    # ===== FORGET DATA (UNMODIFIED) =====
    def forget_data(self):
        files_deleted = 0
        for root_dir, _, files in os.walk(DATA_DIR, topdown=False):
            for name in files:
                try:
                    os.remove(os.path.join(root_dir, name))
                    files_deleted += 1
                except Exception:
                    pass
        
        # Note: The 'self.screen_history' line assumes Processor state is handled
        # in the GUI, but since it's an external thread, clearing the file system
        # is the main step.
        self.status_label.config(text=f"Status: Cleared {files_deleted} files 🧹", fg="gray")
        messagebox.showinfo("Done", "All captured data deleted.")


if __name__ == "__main__":
    try:
        # Check to ensure classes are defined correctly before starting GUI
        _ = ScreenCapturer
        _ = AudioCapturer # Check for AudioCapturer as well
        _ = Processor
        
        root = tk.Tk()
        app = AGIAssistantApp(root)
        root.mainloop()
        
    except NameError:
        messagebox.showerror("Setup Error", "Required classes (ScreenCapturer, AudioCapturer, Processor) not found. Ensure 'capture.py' and 'process.py' files exist and are correctly defined.")

    except ImportError as e:
        messagebox.showerror("Import Error", f"A required module failed to import. Check installation/filenames: {e}")