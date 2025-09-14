# File: convert_to_myVoice.py
import os
import sys
import argparse
import time
from TTS.api import TTS

# ----------------- Force UTF-8 -----------------
os.environ['PYTHONIOENCODING'] = 'utf-8'
sys.stdout.reconfigure(encoding='utf-8')

# ----------------- Arguments -----------------
parser = argparse.ArgumentParser(description="Convert text to cloned voice audiobook")
parser.add_argument("--input", required=True, help="Path to input text file")
parser.add_argument("--voice", required=True, help="Path to voice sample WAV")
parser.add_argument("--output_dir", required=True, help="Folder to save audio chunks")
parser.add_argument("--chunk_size", type=int, default=400, help="Number of words per chunk")
args = parser.parse_args()

INPUT_TEXT = os.path.abspath(args.input)
VOICE_FILE = os.path.abspath(args.voice)
AUDIO_DIR = os.path.abspath(args.output_dir)
CHUNK_SIZE = args.chunk_size

# ----------------- Verify files -----------------
if not os.path.exists(INPUT_TEXT):
    print(f"❌ Input text file not found: {INPUT_TEXT}")
    sys.exit(1)
if not os.path.exists(VOICE_FILE):
    print(f"❌ Voice file not found: {VOICE_FILE}")
    sys.exit(1)
os.makedirs(AUDIO_DIR, exist_ok=True)

# ----------------- Read text and split -----------------
with open(INPUT_TEXT, "r", encoding="utf-8") as f:
    full_text = f.read()

words = full_text.split()
chunks = [" ".join(words[i:i+CHUNK_SIZE]) for i in range(0, len(words), CHUNK_SIZE)]
print(f"✂️ Split text into {len(chunks)} chunks")

# ----------------- Initialize YourTTS -----------------
try:
    print("🔊 Loading YourTTS model (may take a minute)...")
    tts = TTS("tts_models/multilingual/multi-dataset/your_tts", gpu=False)
    print("✅ Model loaded successfully")
except Exception as e:
    print(f"❌ Failed to load TTS model: {e}")
    sys.exit(1)

# ----------------- Generate chunks -----------------
successful_chunks = 0
for i, chunk in enumerate(chunks):
    output_path = os.path.join(AUDIO_DIR, f"chunk_{i}.wav")
    print(f"[{i+1}/{len(chunks)}] Generating audio chunk...")
    try:
        tts.tts_to_file(
            text=chunk,
            speaker_wav=VOICE_FILE,
            language="en",
            file_path=output_path
        )
        successful_chunks += 1
        print(f"✅ Saved: {output_path}")
        time.sleep(0.5)  # avoid CPU overload
    except Exception as e:
        print(f"❌ Failed chunk {i+1}: {e}")
        continue

print(f"\n🎉 Finished generating {successful_chunks}/{len(chunks)} chunks in {AUDIO_DIR}")
