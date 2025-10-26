# =============================================================================
# 1. IMPORTS
# Standard Python libraries and external dependencies
# =============================================================================
import os
import threading
import time
from queue import Queue
from datetime import datetime
import numpy as np
from mss import mss
from PIL import Image
import sounddevice as sd
import soundfile as sf

# =============================================================================
# 2. CONFIGURATION & DIRECTORY SETUP
# Define paths for saving captured data (screenshots and audio placeholders)
# =============================================================================
DATA_DIR = os.path.join(os.getcwd(), "data")
SCREEN_DIR = os.path.join(DATA_DIR, "screenshots")
AUDIO_DIR = os.path.join(DATA_DIR, "audio")

# Create necessary directories if they do not exist
os.makedirs(SCREEN_DIR, exist_ok=True)
os.makedirs(AUDIO_DIR, exist_ok=True)


# =============================================================================
# 3. CAPTURER CLASSES (THREADED WORKERS)
# =============================================================================
class ScreenCapturer(threading.Thread):
    def __init__(self, out_queue: Queue, interval=2.0):
        # Initialize the thread as a daemon so it doesn't block program exit
        super().__init__(daemon=True)
        self.interval = interval  # Time delay between captures
        self.out_queue = out_queue  # Queue to push metadata to main process
        self.running = threading.Event()  # Event flag to control thread execution
        self.sct = None # Placeholder, initialized in run()

    # --- Thread Control Methods ---
    def start_capture(self):
        self.running.set()
        if not self.is_alive():
            self.start()

    def stop_capture(self):
        self.running.clear()

    # --- Thread Execution Loop ---
    def run(self):
        # FIX: Initialize mss here, inside the thread's execution context.
        try:
            self.sct = mss() 
        except Exception as e:
            print(f"Error initializing mss in worker thread: {e}")
            self.running.clear()
            return
            
        # Main loop that executes the capture routine
        while True:
            # Only proceed if the running event is set
            if self.running.is_set():
                try:
                    # 1. Generate timestamp and filename
                    ts = datetime.utcnow().isoformat() + "Z"
                    filename = os.path.join(SCREEN_DIR, f"ss_{int(time.time())}.png")

                    # 2. Capture the screen (using monitor 0, typically the primary)
                    sct_img = self.sct.grab(self.sct.monitors[0])
                    
                    # 3. Convert raw capture data to a PIL Image object
                    img = Image.frombytes("RGB", sct_img.size, sct_img.rgb)
                    
                    # 4. Save the image file
                    img.save(filename)
                    
                    # 5. Push screenshot metadata to the output queue
                    self.out_queue.put({"type": "screenshot", "ts": ts, "path": filename})
                    
                except Exception as e:
                    # Handle errors during capture gracefully
                    print(f"Screen capture error: {e}")
                
                # Wait for the specified interval before the next capture
                time.sleep(self.interval)
            else:
                break


class AudioCapturer(threading.Thread):
    def __init__(self, out_queue: Queue, duration=3, samplerate=16000):
        super().__init__(daemon=True)
        self.out_queue = out_queue
        self.duration = duration
        self.samplerate = samplerate
        self.running = threading.Event()

    def start_capture(self):
        self.running.set()
        if not self.is_alive():
            self.start()

    def stop_capture(self):
        # To stop sounddevice recording, you'd typically need a more complex stream
        # setup, but for this simple polling loop, clearing the event is sufficient.
        self.running.clear()

    def run(self):
        print("Audio capture thread started...")
        while True:
            if self.running.is_set():
                try:
                    # Record a short clip
                    ts = datetime.utcnow().isoformat() + "Z"
                    filename = os.path.join(AUDIO_DIR, f"audio_{int(time.time())}.wav")
                    
                    # Record audio
                    audio = sd.rec(int(self.duration * self.samplerate),
                                   samplerate=self.samplerate,
                                   channels=1, dtype='float32')
                    sd.wait() # Wait until recording is finished
                    
                    # Write to file
                    sf.write(filename, audio, self.samplerate)
                    
                    self.out_queue.put({"type": "audio", "ts": ts, "path": filename})
                    print(f"[AUDIO] Saved chunk: {filename}")

                except Exception as e:
                    print(f"Audio capture error: {e}")
                    # Introduce a pause after an error to prevent a rapid loop
                    time.sleep(1)

                # Wait for the specified duration before the next capture
                time.sleep(self.duration)
            else:
                break

# =============================================================================
# 4. MAIN EXECUTION BLOCK (DEMO)
# Starts both the ScreenCapturer and AudioCapturer
# =============================================================================
if __name__ == "__main__":
    from queue import Queue 
    
    q = Queue()
    
    # Initialize both capturers
    sc = ScreenCapturer(q, interval=1.5)
    ac = AudioCapturer(q, duration=3.0) # Audio chunks every 3 seconds
    
    # Start both threads
    sc.start_capture()
    ac.start_capture()
    
    print("\n--- Capture Started ---")
    print(f"Screenshots every {sc.interval}s, Audio every {ac.duration}s. Press Ctrl+C to stop.")
    
    try:
        # Loop to consume items pushed onto the queue by both worker threads
        while True:
            # Use a timeout to allow the main thread to be responsive to KeyboardInterrupt
            item = q.get(timeout=0.5) 
            print(f"Queue item received: {item['type']} at {os.path.basename(item['path'])}")
            
    except Exception:
        # This catches KeyboardInterrupt and other potential exceptions from q.get()
        pass
        
    finally:
        print("\nStopping capture threads...")
        # Gracefully stop both capture threads
        sc.stop_capture()
        ac.stop_capture()
        
        # Give a moment for threads to terminate
        sc.join(timeout=1.0)
        ac.join(timeout=1.0)
        
        print("--- Capture Stopped ---")