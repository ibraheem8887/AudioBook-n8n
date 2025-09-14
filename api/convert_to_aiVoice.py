# file: pyttsx3_audiobook_fast.py

import pyttsx3
import os
import time
import sys
import argparse

sys.stdout.reconfigure(encoding='utf-8')

# ----------------- Command-line Arguments -----------------
parser = argparse.ArgumentParser(description="Convert text file to audiobook using pyttsx3")
parser.add_argument("--input", required=True, help="Path to input text file")
parser.add_argument("--output", required=True, help="Path to output audio file")
args = parser.parse_args()

TEXT_FILE = os.path.normpath(args.input)
OUTPUT_AUDIO = os.path.normpath(args.output)

# ----------------- Functions -----------------
def read_text(file_path):
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"{file_path} not found!")
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()

def text_to_speech_fast(text, output_file):
    engine = pyttsx3.init()

    # Adjust voice and speed
    voices = engine.getProperty('voices')
    engine.setProperty('voice', voices[0].id)  # 0=male, 1=female
    engine.setProperty('rate', 150)            # words per minute

    print("🔊 Starting audiobook conversion for entire book...")

    start_time = time.time()
    engine.save_to_file(text, output_file)
    engine.runAndWait()
    elapsed = time.time() - start_time

    print(f"✅ Audiobook completed and saved as {output_file}")
    print(f"⏱ Total time taken: {int(elapsed // 60)} min {int(elapsed % 60)} sec")

# ----------------- Main -----------------
if __name__ == "__main__":
    full_text = read_text(TEXT_FILE)
    text_to_speech_fast(full_text, OUTPUT_AUDIO)
