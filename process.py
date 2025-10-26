# =============================================================================
# 1. IMPORTS
# All necessary modules for the code snippet to function
# =============================================================================
import os
import time
import json
import threading
from queue import Queue
from datetime import datetime
from PIL import Image
# External libraries required: opencv-python, pytesseract, Pillow (PIL)
import pytesseract
import cv2


# =============================================================================
# 2. CONFIGURATION (Placeholder constants)
# These constants define directories used in the original snippet.
# =============================================================================
DATA_DIR = os.path.join(os.getcwd(), "data")
SCREEN_DIR = os.path.join(DATA_DIR, "screenshots")
os.makedirs(SCREEN_DIR, exist_ok=True) # Ensure directory exists for the main block


# =============================================================================
# 3. PROCESSOR CLASS (Incorporates the provided snippet)
# This class defines the structure where the logic snippet resides.
# =============================================================================
class Processor(threading.Thread):
    def __init__(self, in_queue: Queue, out_file="processed_events.jsonl"):
        super().__init__(daemon=True)
        self.in_queue = in_queue
        self.out_file = os.path.join(DATA_DIR, out_file)
        self.running = threading.Event()
        self.screen_history = []  # Stores paths for frame-diff
    
    # Placeholder for the event inference logic
    def infer_events_from_ocr(self, text: str) -> list:
        """Analyzes OCR text to infer user actions."""
        return ["Text detected" if text.strip() else "No significant text"]

    def start_processing(self):
        self.running.set()
        if not self.is_alive():
            self.start()

    def stop_processing(self):
        self.running.clear()
    
    def run(self):
        # Main thread loop
        while True:
            # Check if processing is active
            if self.running.is_set():
                # Block to get item from queue
                try:
                    item = self.in_queue.get(timeout=0.1) # Use a timeout for responsiveness
                except Exception:
                    time.sleep(0.1)
                    continue

                if item["type"] == "screenshot":
                    path = item["path"]
                    ts = item["ts"]
                    
                    # Read image
                    try:
                        img = Image.open(path)
                        gray = img.convert("L")
                    except FileNotFoundError:
                        print(f"File not found: {path}")
                        self.in_queue.task_done()
                        continue
                        
                    # Run OCR
                    try:
                        text = pytesseract.image_to_string(gray)
                    except Exception as e:
                        text = ""
                    
                    events = self.infer_events_from_ocr(text)
                    
                    # simple frame-diff with last frame to detect major change
                    change_score = 0.0
                    if self.screen_history:
                        last_path = self.screen_history[-1]
                        last = cv2.imread(last_path)
                        cur = cv2.imread(path)
                        
                        if last is not None and cur is not None:
                            try:
                                last_gray = cv2.cvtColor(last, cv2.COLOR_BGR2GRAY)
                                cur_gray = cv2.cvtColor(cur, cv2.COLOR_BGR2GRAY)
                                
                                # resize to same
                                h = min(last_gray.shape[0], cur_gray.shape[0])
                                w = min(last_gray.shape[1], cur_gray.shape[1])
                                last_r = cv2.resize(last_gray, (w, h))
                                cur_r = cv2.resize(cur_gray, (w, h))
                                
                                diff = cv2.absdiff(last_r, cur_r)
                                change_score = float(diff.mean())
                            except Exception:
                                change_score = 0.0 # Failed calculation
                                
                    self.screen_history.append(path)
                    
                    record = {
                        "ts": ts,
                        "type": "screenshot_processed",
                        "path": path,
                        "ocr_text": text.strip(),
                        "inferred_events": events,
                        "frame_change_score": change_score,
                    }
                    
                    # append to output file as JSONL
                    with open(self.out_file, "a", encoding="utf-8") as f:
                        f.write(json.dumps(record, ensure_ascii=False) + "\n")
                        
                    print(f"Processed {os.path.basename(path)} -> events:{len(events)} change:{change_score:.2f}")

                # Crucial: Signal that the item has been processed
                self.in_queue.task_done()

            else:
                # idle wait when running is false
                time.sleep(0.2)


# =============================================================================
# 4. MAIN EXECUTION BLOCK (Driver logic)
# Corrected for proper scope and imports.
# =============================================================================
if __name__ == "__main__":
    from queue import Queue
    
    # NOTE: The original logic here is a *test harness* for monitoring a directory
    # and feeding the queue, simulating a capturer's output.
    
    q = Queue()
    p = Processor(q)
    p.start_processing()
    
    print("Processor started. Feed queue with screenshot items.")
    
    # simple test: monitor screenshots folder and process new files
    seen = set()
    while True:
        try:
            for fname in sorted(os.listdir(SCREEN_DIR)):
                full = os.path.join(SCREEN_DIR, fname)
                if full not in seen and fname.lower().endswith(".png"):
                    seen.add(full)
                    # NOTE: datetime.utcnow() is now available due to main block setup
                    q.put({"type": "screenshot", "ts": datetime.utcnow().isoformat() + "Z", "path": full})
            time.sleep(1.0)
            
        except KeyboardInterrupt:
            p.stop_processing()
            q.join()
            print("Monitoring stopped.")
            break
        except Exception as e:
            print(f"Main loop error: {e}")
            time.sleep(5)