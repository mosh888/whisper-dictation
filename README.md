# Whisper Dictation

A lightweight, fully offline AI dictation tool for Windows. Hold a hotkey anywhere on your system, speak, release, and the transcribed text is typed directly into whatever app is in focus — no cloud, no subscription, no terminal window.

Built on [faster-whisper](https://github.com/SYSTRAN/faster-whisper) and runs silently in the system tray.

---

## Features

- Fully local — audio never leaves your machine
- System-wide hotkey (works in any app)
- Runs silently in the system tray with a colour-coded status icon
- Auto-starts with Windows
- Configurable model size and hotkey

---

## Requirements

- Windows 10/11
- Python 3.9+
- A microphone

---

## Installation

**1. Clone the repo**
```bash
git clone https://github.com/mosh888/whisper-dictation
cd whisper-dictation
```

**2. Install dependencies**
```bash
pip install faster-whisper sounddevice numpy pyperclip keyboard pystray pillow scipy
```

**3. Run it**
```bash
pythonw dictation.py
```

A grey circle will appear in your system tray — the app is ready.

> On first run, the Whisper model will be downloaded automatically (~500MB for `small`, ~1.5GB for `medium`).

---

## Usage

| Action | Result |
|--------|--------|
| Hold **Right Ctrl + Right Alt** | Starts recording (icon turns red) |
| Release both keys | Stops recording, transcribes (icon turns orange), types result |
| Right-click tray icon → Exit | Quits the app |

The transcribed text is pasted wherever your cursor is — works in any text field, editor, browser, terminal, etc.

---

## Configuration

Edit the config section at the top of `dictation.py`:

```python
# --- Config ---
MODEL_SIZE = "small"              # tiny, base, small, medium, large-v3-turbo
RECORD_KEYS = {"right ctrl", "right alt"}  # hold both to record
SAMPLE_RATE = 16000               # Whisper expects 16kHz
# --------------
```

### Available models

| Model | Size | Speed | Accuracy |
|-------|------|-------|----------|
| `tiny` | 75MB | Fastest | Low |
| `base` | 145MB | Fast | OK |
| `small` | 465MB | Fast | Good |
| `medium` | 1.5GB | Moderate | Great |
| `large-v3-turbo` | 1.6GB | Fast | Excellent |

`small` is recommended for most laptops. `large-v3-turbo` is the best quality option if your machine can handle it.

### Custom hotkey examples

```python
RECORD_KEYS = {"scroll lock"}          # single key
RECORD_KEYS = {"right ctrl", "right alt"}  # combo (default)
RECORD_KEYS = {"f9"}                   # function key
```

---

## Auto-start with Windows

A `launch_dictation.vbs` file is included. To have dictation start automatically on login:

1. Press `Win + R`, type `shell:startup`, press Enter
2. Copy `launch_dictation.vbs` into that folder

That's it — the app will launch silently on every login.

---

## How it works

1. `keyboard` library listens for the hotkey system-wide
2. `sounddevice` captures audio from the default microphone at 16kHz
3. `faster-whisper` transcribes the audio locally using the Whisper model
4. `pyperclip` + `keyboard` paste the result into the active window
5. `pystray` manages the system tray icon and graceful exit

---

## Dependencies

| Package | Purpose |
|---------|---------|
| `faster-whisper` | Local Whisper speech-to-text inference |
| `sounddevice` | Microphone audio capture |
| `numpy` | Audio data handling |
| `scipy` | WAV file writing |
| `keyboard` | Global hotkey detection and text injection |
| `pyperclip` | Clipboard management |
| `pystray` | System tray icon |
| `pillow` | Tray icon image generation |

---

## License

MIT
