# AGI Activity Monitor & Automation Prototype

## 💡 Project Overview

This project is a Python-based prototype application designed to monitor and analyze user activity on a desktop environment, generate summaries of common workflows, and provide an interface to run simple, recorded automations.

It functions as a full-stack proof-of-concept, integrating three main components:

1.  **Activity Capturer (`capture.py`):** Continuously captures screenshots and audio snippets from the user's desktop.
2.  **Data Processor (`process.py`):** Consumes captured data, runs **Optical Character Recognition (OCR)** to extract text, detects significant screen changes, and logs structured workflow events.
3.  **Analysis & Automation (`summarize.py` & `automation_runner.py`):** Analyzes the logged events to identify common user workflows and provides an interface (`app.py`) to execute simple, pre-defined automations.

## 🛠️ Installation & Setup

### Prerequisites

You must have **Python 3.x** installed. The project relies on several external libraries, notably `opencv-python` and `pytesseract`, which require specific system setup for OCR functionality.

1.  **Tesseract OCR Engine:**
      * This project requires the **Tesseract OCR engine** to be installed on your system.
      * Download and install the official Tesseract executable from the project site.
      * **Crucially:** Add the installation directory (e.g., `C:\Program Files\Tesseract-OCR`) to your system's **PATH** environment variable.

### Project Setup

1.  **Clone the Repository (or save the files):**

    ```bash
    git clone [YOUR-REPO-URL]
    cd [YOUR-PROJECT-DIRECTORY]
    ```

2.  **Create a Virtual Environment (Recommended):**

    ```bash
    python -m venv venv
    .\venv\Scripts\activate  # On Windows
    source venv/bin/activate  # On macOS/Linux
    ```

3.  **Install Dependencies:**
    Use the following command to install all the required packages based on your list:

    ```bash
    pip install certifi cffi charset-normalizer colorama idna MouseInfo mss numpy opencv-python packaging pillow PyAutoGUI pycparser PyGetWindow PyMsgBox pyperclip PyRect PyScreeze PySimpleGUI pytesseract pytweening PyYAML requests scipy sounddevice soundfile srt tqdm urllib3 vosk watchdog websockets
    ```

    *(Note: This single command installs all the specific versions you listed.)*

## 🚀 Usage

### 1\. File Structure

The application expects the following file structure to run correctly:

```
/
├── app.py                  # Main GUI and control center
├── capture.py              # Screen and Audio Capturer threads
├── process.py              # Data Processor thread (OCR, frame diff)
├── summarize.py            # Workflow analysis logic
├── automation_runner.py    # PyAutoGUI automation execution
└── /data/                  # Automatically created directory for logs and media
    ├── screenshots/        # Captured PNG files
    ├── audio/              # Captured WAV files
    └── processed_events.jsonl # Log of all processed activities
```

### 2\. Running the Application

Start the main application via the `app.py` file:

```bash
python app.py
```
For build/.exe
```bash
pyinstaller --noconsole --onefile app.py
```

### 3\. Workflow

The application runs through four main stages controlled by the GUI:

| Stage | Action | Component(s) | Purpose |
| :--- | :--- | :--- | :--- |
| **Capture** | Click **"▶ Start Capture"** | `capture.py`, `process.py` | Starts simultaneous, multi-threaded screen/audio capture and real-time processing/logging of events. |
| **Stop** | Click **"⏹ Stop Capture"** | `capture.py`, `process.py` | Gracefully stops the background threads. |
| **Analyze** | Click **"⚙ Process & Summarize"** | `summarize.py` | Reads the raw logs from `/data/processed_events.jsonl`, groups similar event sequences, and produces a summary of suggested workflows in `/data/workflow_summaries.json`. |
| **Automate** | Click **"🤖 Run Automation"** | `automation_runner.py` | Executes a small, pre-defined sequence of mouse/keyboard actions using `PyAutoGUI` as a proof of concept for running learned workflows. |

## 📦 Key Technologies and Dependencies

The extensive list of installed libraries covers several core functionalities:

| Functionality | Key Library | What it's For |
| :--- | :--- | :--- |
| **GUI** | **PySimpleGUI** | Provides the simple desktop interface (`app.py`). |
| **Screen Capture** | **mss** | Efficiently captures raw screenshot data. |
| **Audio Capture** | **sounddevice** | Captures audio streams from the microphone. |
| **OCR (Text Extraction)** | **pytesseract** | Extracts text content from captured screenshots. |
| **Image/Video Processing** | **opencv-python**, **Pillow** | Used for reading images, converting formats, and calculating screen change scores (`process.py`). |
| **Automation** | **PyAutoGUI** | Executes mouse movements, clicks, and keystrokes (`automation_runner.py`). |
| **Speech Recognition** | **vosk** | A lightweight, offline speech recognition toolkit for processing captured audio clips. |
| **File Monitoring** | **watchdog** | Can be used (though not fully implemented in the current flow) to monitor the creation of new files/events. |
| **Data Handling** | **numpy, scipy, PyYAML, requests** | Standard tools for scientific computing, data array manipulation, configuration, and network communication. |