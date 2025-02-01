## **Phase 1: Requirements & Architecture**

### **Key Functional Requirements:**

1. **Recording:**  
   * A simple “Record” button that starts and stops audio capture.  
   * Save the audio in a common format (e.g., WAV).  
2. **Transcription:**  
   * Run Whisper (or a lightweight variant like the `tiny`/`small` model) locally on the recorded file.  
   * Display the transcription in a clear, scrollable text area.  
3. **Manual Extraction:**  
   * The user reviews the transcript and extracts key info manually (e.g., by copying text into a separate note field).  
   * No need to store the raw transcript permanently.  
4. **Secure Deletion:**  
   * Once the user confirms they’ve extracted the necessary info, provide a “Secure Delete” function.  
   * Use secure deletion methods (overwriting file content) to ensure data is irrecoverable.  
5. **Optional (for further iterations):**  
   * Provide status logs (without storing PHI) for audit and debugging purposes.  
   * Simple user authentication (a password or PIN) to lock the app if needed.

### **Key Non-Functional Requirements:**

* **Local Processing Only:** All transcription is done offline.  
* **HIPAA-Oriented:** Minimize storage of PHI; use encryption for temporary data and secure deletion.  
* **Simplicity:** The UI should be minimalist, targeting non-tech-savvy users.

### **High-Level Architecture:**

* **Frontend (UI):**  
  1. A desktop application (using Python with PyQt5/**PySide6** or Electron for a cross-platform solution).  
* **Backend (Processing):**  
  1. Python scripts to handle audio recording (**SoundDevice**), running Whisper, and secure deletion.  
* **Data Flow:**  
  1. Record audio → 2\. Save file (temporarily, encrypted if possible) → 3\. Transcribe using Whisper → 4\. Display transcript → 5\. User manually extracts key info → 6\. App securely deletes temporary files.

---

## **Phase 1: Requirements & Architecture**

### **Key Functional Requirements:**

1. **Recording:**  
   * A simple “Record” button that starts and stops audio capture.  
   * Save the audio in a common format (e.g., WAV).  
2. **Transcription:**  
   * Run Whisper (or a lightweight variant like the `tiny`/`small` model) locally on the recorded file.  
   * Display the transcription in a clear, scrollable text area.  
3. **Manual Extraction:**  
   * The user reviews the transcript and extracts key info manually (e.g., by copying text into a separate note field).  
   * No need to store the raw transcript permanently.  
4. **Secure Deletion:**  
   * Once the user confirms they’ve extracted the necessary info, provide a “Secure Delete” function.  
   * Use secure deletion methods (overwriting file content) to ensure data is irrecoverable.  
5. **Optional (for further iterations):**  
   * Provide status logs (without storing PHI) for audit and debugging purposes.  
   * Simple user authentication (a password or PIN) to lock the app if needed.

### **Key Non-Functional Requirements:**

* **Local Processing Only:** All transcription is done offline.  
* **HIPAA-Oriented:** Minimize storage of PHI; use encryption for temporary data and secure deletion.  
* **Simplicity:** The UI should be minimalist, targeting non-tech-savvy users.

### **High-Level Architecture:**

* **Frontend (UI):**  
  1. A desktop application (using Python with PyQt5/PySide6 or Electron for a cross-platform solution).  
* **Backend (Processing):**  
  1. Python scripts to handle audio recording, running Whisper, and secure deletion.  
* **Data Flow:**  
  1. Record audio → 2\. Save file (temporarily, encrypted if possible) → 3\. Transcribe using Whisper → 4\. Display transcript → 5\. User manually extracts key info → 6\. App securely deletes temporary files.

---

## **Phase 2: Choosing Tools & Setup**

### **Programming Language & Frameworks:**

* **Python:**  
  * Widely supported, plenty of libraries for audio (PyAudio, sounddevice) and UI (PyQt5/PySide6).  
* **Audio Recording:**  
  * `PyAudio` or `sounddevice` for capturing audio. Sounddevice sounds better  
* **Transcription:**  
  * The `openai-whisper` package (or its optimized fork, if available) for transcription.  
* **UI Framework:**  
  * **PyQt5/PySide6:** For a desktop GUI. PySide6 sounds like a better choice.  
* **Secure Deletion:**  
  * Python-based file overwrite routines (using `os.urandom` and careful file handling).

### **Development Environment Setup:**

**Create a virtual environment:**

`python -m venv transcription_env`  
`source transcription_env/bin/activate  # or transcription_env\Scripts\activate on Windows`

1. 

**Install dependencies:**  
bash  
Copy  
`pip install openai-whisper pyaudio PyQt5 cryptography`

2. *(Adjust packages as needed. For audio recording, you might try `sounddevice` if PyAudio is troublesome.)*  
3. **Download the Whisper model:**  
   * You can download a small model (e.g., `tiny` or `small`) to keep processing fast.

## **Phase 3: Building the MVP**

### **Step 1: Audio Recording Module**

* **Objective:** Capture a 10-minute (or shorter) audio clip.  
* **Implementation:**  
  * Use `PyAudio` to open an audio stream.  
  * Create a simple interface with a “Record” button.  
  * Save the audio as `session.wav` in a temporary folder.

### **Step 2: Transcription Module**

* **Objective:** Run Whisper on the recorded file.  
* **Implementation:**  
  * Use the `whisper` Python package to transcribe `session.wav`.  
  * Display the transcription in a text box in the UI.

### **Step 3: UI Integration**

* **Objective:** Build a GUI that ties it all together.  
* **Implementation:**  
  * Create a window with buttons: **Record**, **Transcribe**, **Secure Delete**.  
  * Display areas: one for showing transcription results, one for status messages.  
  * Use PyQt5 signals and slots to connect button presses to functions.

*High-Level UI Flow:*

1. **User clicks “Record”**: The app starts recording audio.  
2. **After recording**, user clicks **“Transcribe”**: The app processes the file and shows text.  
3. **User extracts key info manually**.  
4. **User clicks “Secure Delete”**: The app runs the secure deletion function.

### **Step 4: Secure Deletion Module**

* **Objective:** Ensure that once the session is over, the audio and transcript files are securely deleted.  
* **Implementation:**  
  * Write a function that opens the file in binary mode, overwrites it with random data, and then deletes it.

---

## **Phase 4: Testing and Iteration**

### **Testing:**

1. **Functionality Testing:**  
   * Test recording for various durations.  
   * Check that transcription runs accurately and quickly.  
   * Verify that the UI is intuitive.  
2. **Security Testing:**  
   * Test the secure deletion on different operating systems.  
   * Ensure that no temporary files are left behind (check OS temp directories).  
3. **User Testing:**  
   * Ideally, have a few users (or simulate a speech therapist’s workflow) to see if the flow makes sense.  
   * Get feedback on the UI and performance.

### **Iteration:**

* Tweak performance (switch between Whisper models if needed).  
* Improve UI responsiveness.  
* Consider adding logs or error handling for secure deletion failures.  
* Document any manual steps the user must follow to keep their environment secure (like OS-level encryption).

---

## **Phase 5: Packaging & Distribution**

### **Packaging:**

* **For Windows:**  
  * Use **PyInstaller** to package the app into an EXE.

`pyinstaller --onefile --hidden-import=whisper main.py`

* **For Mac:**  
  * Use PyInstaller or create a DMG.  
* **Bundle Dependencies:**  
  * Ensure that FFmpeg (required by Whisper) is either bundled or auto-installed during first run.

### **Distribution Considerations:**

* Provide clear instructions regarding device security and best practices for handling PHI.  
* Include the MIT License and attribution for Whisper.
