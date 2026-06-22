"""
Local Whisper Dictation Script
-------------------------------
Hold Right Ctrl + Right Alt to record, release to transcribe and type the result.
Runs silently in the system tray.

Requirements:
    pip install faster-whisper sounddevice numpy pyperclip keyboard pystray pillow
"""

import threading
import tempfile
import os
import numpy as np
import sounddevice as sd
import keyboard
import pyperclip
from faster_whisper import WhisperModel
import pystray
from PIL import Image, ImageDraw

# --- Config ---
MODEL_SIZE = "small"         # tiny, base, small, medium, large-v3-turbo
RECORD_KEYS = {"right ctrl", "right alt"}  # hold both to record
SAMPLE_RATE = 16000          # Whisper expects 16kHz
# --------------

print(f"Loading Whisper '{MODEL_SIZE}' model (downloads on first run, ~1.5GB)...")
model = WhisperModel(MODEL_SIZE, device="cpu", compute_type="int8")
print(f"Model ready [{MODEL_SIZE}]. Hold Right Ctrl + Right Alt to dictate, release to transcribe.\n")

recording = False
audio_frames = []
lock = threading.Lock()


def record_audio():
    """Capture audio from mic while recording flag is True."""
    global audio_frames
    with sd.InputStream(samplerate=SAMPLE_RATE, channels=1, dtype="float32") as stream:
        while recording:
            chunk, _ = stream.read(1024)
            with lock:
                audio_frames.append(chunk.copy())


def transcribe_and_type():
    """Transcribe the recorded audio and type it into the active window."""
    with lock:
        frames = list(audio_frames)

    if not frames:
        return

    audio = np.concatenate(frames, axis=0).flatten()

    # Save to a temp wav file (faster-whisper needs a file or numpy array)
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
        tmp_path = f.name

    import scipy.io.wavfile as wav
    wav.write(tmp_path, SAMPLE_RATE, audio)

    print("Transcribing...", end=" ", flush=True)
    segments, info = model.transcribe(tmp_path, beam_size=5)
    text = " ".join(seg.text.strip() for seg in segments).strip()
    os.unlink(tmp_path)

    if text:
        print(f'"{text}"')
        pyperclip.copy(text)
        keyboard.send("ctrl+v")
    else:
        print("(no speech detected)")


def on_hotkey_press():
    global recording, audio_frames
    if recording:
        return
    recording = True
    audio_frames = []
    print("Recording... (release Right Ctrl + Right Alt to stop)")
    threading.Thread(target=record_audio, daemon=True).start()


def on_hotkey_release():
    global recording
    if not recording:
        return
    recording = False
    threading.Thread(target=transcribe_and_type, daemon=True).start()


_keys_down = set()

def _on_event(event):
    if event.name not in RECORD_KEYS:
        return
    if event.event_type == "down":
        _keys_down.add(event.name)
        if _keys_down >= RECORD_KEYS:
            on_hotkey_press()
    elif event.event_type == "up":
        was_full = _keys_down >= RECORD_KEYS
        _keys_down.discard(event.name)
        if was_full:
            on_hotkey_release()

keyboard.hook(_on_event)


def make_icon(color):
    img = Image.new("RGB", (64, 64), color="black")
    draw = ImageDraw.Draw(img)
    draw.ellipse([8, 8, 56, 56], fill=color)
    return img


icon = pystray.Icon(
    "WhisperDictation",
    make_icon("grey"),
    "Whisper Dictation — Ready",
    menu=pystray.Menu(
        pystray.MenuItem("Whisper Dictation", None, enabled=False),
        pystray.MenuItem(f"Model: {MODEL_SIZE}", None, enabled=False),
        pystray.MenuItem("Exit", lambda icon, item: icon.stop()),
    ),
)


def update_icon(color, tooltip):
    icon.icon = make_icon(color)
    icon.title = tooltip


# Patch on_hotkey_press/release to update tray icon
_orig_press = on_hotkey_press
_orig_release = on_hotkey_release

def on_hotkey_press():
    update_icon("red", "Whisper Dictation — Recording...")
    _orig_press()

def on_hotkey_release():
    update_icon("orange", "Whisper Dictation — Transcribing...")
    _orig_release()

# Re-hook with updated functions
keyboard.unhook_all()

def _on_event(event):
    if event.name not in RECORD_KEYS:
        return
    if event.event_type == "down":
        _keys_down.add(event.name)
        if _keys_down >= RECORD_KEYS:
            on_hotkey_press()
    elif event.event_type == "up":
        was_full = _keys_down >= RECORD_KEYS
        _keys_down.discard(event.name)
        if was_full:
            on_hotkey_release()

keyboard.hook(_on_event)

# Patch transcribe_and_type to reset icon when done
_orig_transcribe = transcribe_and_type

def transcribe_and_type():
    _orig_transcribe()
    update_icon("grey", "Whisper Dictation — Ready")

icon.run()
