# file: main.py

from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import JSONResponse, FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
import os
import subprocess
import uuid
import shutil
import logging
import tempfile
import logging
from logging.handlers import RotatingFileHandler
import os

os.makedirs("logs", exist_ok=True)

handler = RotatingFileHandler("logs/server.log", maxBytes=10_000_000, backupCount=5)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[handler]
)

# ------------------- Setup -------------------
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

app = FastAPI(title="PDF to Audiobook API (AI / Cloned Voice)")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
BOOK_DIR = os.path.join(BASE_DIR, "book_texts")
AUDIO_DIR = os.path.join(BASE_DIR, "audio_output")
CHUNK_DIR = os.path.join(BASE_DIR, "audio_chunks")
VOICE_SAMPLE_DIR = os.path.join(BASE_DIR, "myVoice")  # Store uploaded voice samples

# Ensure directories exist
os.makedirs(BOOK_DIR, exist_ok=True)
os.makedirs(AUDIO_DIR, exist_ok=True)
os.makedirs(CHUNK_DIR, exist_ok=True)
os.makedirs(VOICE_SAMPLE_DIR, exist_ok=True)

# Scripts
EXTRACT_PDF_SCRIPT = os.path.join(BASE_DIR, "extract_pdf_text.py")
CONVERT_AI_SCRIPT = os.path.join(BASE_DIR, "convert_to_aiVoice.py")
CONVERT_MY_SCRIPT = os.path.join(BASE_DIR, "convert_to_myVoice.py")
MERGE_AUDIO_SCRIPT = os.path.join(BASE_DIR, "merge_audio.py")

# Valid voices
VALID_VOICES = {"ai", "myvoice"}

# Serve static files
app.mount("/audio", StaticFiles(directory=AUDIO_DIR), name="audio")
app.mount("/voice_samples", StaticFiles(directory=VOICE_SAMPLE_DIR), name="voice_samples")

# ------------------- Home Page -------------------
@app.get("/", response_class=HTMLResponse)
async def home_page():
    return """
    <html>
    <head>
        <title>PDF to Audiobook</title>
        <style>
            body { font-family: Arial, sans-serif; background-color: #f4f4f9; color: #333; margin: 0; padding: 20px; }
            h2 { color: #4a90e2; }
            .container { max-width: 900px; margin: auto; background: #fff; padding: 20px; border-radius: 10px; box-shadow: 0 0 15px rgba(0,0,0,0.1); }
            label { font-weight: bold; }
            input[type="file"], select, button { width: 100%; padding: 10px; margin-top: 5px; margin-bottom: 20px; border-radius: 5px; border: 1px solid #ccc; }
            button { background-color: #4a90e2; color: white; border: none; cursor: pointer; transition: background 0.3s; }
            button:hover { background-color: #357ABD; }
            .text-preview { background: #f0f0f0; padding: 15px; border-radius: 5px; height: 300px; overflow-y: scroll; white-space: pre-wrap; margin-bottom: 20px; }
            .voice-upload { display: none; }
            .audio-player { margin-top: 10px; }
        </style>
        <script>
            async function previewPDFText(event) {
                const fileInput = document.getElementById('pdf_file');
                const formData = new FormData();
                formData.append('pdf_file', fileInput.files[0]);
                const res = await fetch('/extract_pdf_preview', { method: 'POST', body: formData });
                const data = await res.json();
                if (data.error) { alert(data.error); return; }
                document.getElementById('text_preview').textContent = data.text_preview;
                document.getElementById('text_file_hidden').value = data.text_file;
                document.getElementById('audiobook_form').style.display = 'block';
            }

            function toggleVoiceUpload() {
                const type = document.getElementById('voice_type').value;
                document.getElementById('voice_upload').style.display = (type === 'myvoice') ? 'block' : 'none';
            }

            async function generateAudiobook(event) {
                event.preventDefault();
                const form = document.getElementById('audiobook_form');
                const formData = new FormData(form);
                const format = document.getElementById('format').value;
                formData.set('format', format);

                const btn = document.getElementById('generate_btn');
                btn.disabled = true;
                btn.textContent = 'Generating...';

                const res = await fetch('/tts', { method: 'POST', body: formData });
                const data = await res.json();

                btn.disabled = false;
                btn.textContent = 'Generate Audiobook';

                if (data.error) { alert(data.error); return; }

                const playerDiv = document.getElementById('audio_player_div');
                playerDiv.innerHTML = `
                    <h3>Audiobook Ready:</h3>
                    <audio controls class="audio-player">
                        <source src="${data.url}" type="audio/${format}">
                        Your browser does not support the audio element.
                    </audio>
                    <br>
                    <a href="${data.url}" download="audiobook.${format}">Download ${format.toUpperCase()}</a>
                `;
            }
        </script>
    </head>
    <body>
        <div class="container">
            <h2>PDF to Audiobook</h2>
            <label>Upload PDF:</label>
            <input type="file" id="pdf_file" onchange="previewPDFText(event)">

            <h3>Text Preview:</h3>
            <div id="text_preview" class="text-preview">Upload a PDF to see preview...</div>

            <form id="audiobook_form" style="display:none;" onsubmit="generateAudiobook(event)" enctype="multipart/form-data">
                <label>Select Voice:</label>
                <select name="voice_type" id="voice_type" onchange="toggleVoiceUpload()">
                    <option value="ai">AI Voice</option>
                    <option value="myvoice">Cloned Voice</option>
                </select>

                <div id="voice_upload" class="voice-upload">
                    <label>Upload Voice Sample (WAV):</label>
                    <input type="file" name="voice_file" accept=".wav">
                </div>

                <label>Select Format:</label>
                <select name="format" id="format">
                    <option value="mp3">MP3</option>
                    <option value="wav">WAV</option>
                </select>

                <input type="hidden" name="text_file" id="text_file_hidden">
                <button type="submit" id="generate_btn">Generate Audiobook</button>
            </form>

            <div id="audio_player_div"></div>
        </div>
    </body>
    </html>
    """

# ------------------- Health Check -------------------
@app.get("/health")
async def health_check():
    dirs = {
        "book_texts": os.path.exists(BOOK_DIR),
        "audio_output": os.path.exists(AUDIO_DIR),
        "audio_chunks": os.path.exists(CHUNK_DIR),
        "voice_samples": os.path.exists(VOICE_SAMPLE_DIR)
    }
    return {"status": "ok", "directories": dirs}

# ------------------- Extract PDF Preview -------------------
@app.post("/extract_pdf_preview")
async def extract_pdf_preview(pdf_file: UploadFile = File(...)):
    try:
        temp_pdf = os.path.join(tempfile.gettempdir(), f"{uuid.uuid4().hex}.pdf")
        temp_text = os.path.join(BOOK_DIR, f"{uuid.uuid4().hex}_preview.txt")
        with open(temp_pdf, "wb") as f: f.write(await pdf_file.read())

        subprocess.run(["python", EXTRACT_PDF_SCRIPT, "--input", temp_pdf, "--output", temp_text], check=True)
        with open(temp_text, "r", encoding="utf-8") as f: content = f.read()
        os.remove(temp_pdf)

        preview = content[:2000] + ("..." if len(content) > 2000 else "")
        return {"text_preview": preview, "text_file": temp_text}

    except subprocess.CalledProcessError as e:
        logging.error(f"PDF extraction failed: {e.stderr}")
        return JSONResponse(status_code=500, content={"error": f"PDF extraction failed: {e.stderr}"})
    except Exception as e:
        logging.error(str(e))
        return JSONResponse(status_code=500, content={"error": str(e)})

# ------------------- TTS Endpoint -------------------
@app.post("/tts")
async def tts(
    text_file: str = Form(...),
    voice_type: str = Form(...),
    format: str = Form(...),
    voice_file: UploadFile = File(None)
):
    voice_type = voice_type.lower()
    format = format.lower()
    if voice_type not in VALID_VOICES: return JSONResponse(status_code=400, content={"error": f"voice_type must be one of {VALID_VOICES}"})
    if format not in {"mp3", "wav"}: return JSONResponse(status_code=400, content={"error": "format must be mp3 or wav"})
    if not os.path.exists(text_file): return JSONResponse(status_code=404, content={"error": "Text file not found"})

    filename = f"{uuid.uuid4().hex}_audiobook.{format}"
    output_file = os.path.join(AUDIO_DIR, filename)
    voice_sample_path = None

    try:
        if voice_type == "ai":
            subprocess.run(["python", CONVERT_AI_SCRIPT, "--input", text_file, "--output", output_file], check=True)
        elif voice_type == "myvoice":
            if not voice_file: return JSONResponse(status_code=400, content={"error": "Voice sample required for myvoice"})
            voice_sample_path = os.path.join(VOICE_SAMPLE_DIR, f"{uuid.uuid4().hex}_sample.wav")
            with open(voice_sample_path, "wb") as f: f.write(await voice_file.read())
            logging.info(f"Voice sample saved: {voice_sample_path}")

            shutil.rmtree(CHUNK_DIR, ignore_errors=True)
            os.makedirs(CHUNK_DIR, exist_ok=True)

            subprocess.run(["python", CONVERT_MY_SCRIPT, "--input", text_file, "--voice", voice_sample_path, "--output_dir", CHUNK_DIR], check=True)
            subprocess.run(["python", MERGE_AUDIO_SCRIPT], check=True)
            merged_wav = os.path.join(BASE_DIR, "my_voice_audiobook.wav")
            if not os.path.exists(merged_wav): return JSONResponse(status_code=500, content={"error": "Merged audiobook not found"})

            if format == "mp3":
                subprocess.run(["ffmpeg", "-y", "-i", merged_wav, output_file], check=True)
                os.remove(merged_wav)
            else:
                shutil.move(merged_wav, output_file)

            shutil.rmtree(CHUNK_DIR, ignore_errors=True)

        if voice_sample_path and os.path.exists(voice_sample_path): os.remove(voice_sample_path)
        if os.path.exists(text_file): os.remove(text_file)

        return {"url": f"/audio/{filename}"}

    except subprocess.CalledProcessError as e:
        logging.error(f"TTS failed: {e.stderr}")
        return JSONResponse(status_code=500, content={"error": f"TTS process failed: {e.stderr}"})
    except Exception as e:
        logging.error(str(e))
        return JSONResponse(status_code=500, content={"error": str(e)})

# ------------------- List Audiobooks -------------------
@app.get("/list_audiobooks")
async def list_audiobooks():
    files = os.listdir(AUDIO_DIR)
    files = [{"name": f, "url": f"/audio/{f}", "type": f.split(".")[-1]} for f in files]
    return {"audiobooks": files}

# ------------------- Voice Management -------------------
@app.get("/voices")
async def list_voices():
    files = os.listdir(VOICE_SAMPLE_DIR)
    voices = [{"name": f, "url": f"/voice_samples/{f}"} for f in files]
    return {"voices": voices}

@app.delete("/voices/{voice_name}")
async def delete_voice(voice_name: str):
    path = os.path.join(VOICE_SAMPLE_DIR, voice_name)
    if os.path.exists(path):
        os.remove(path)
        return {"status": "deleted", "voice": voice_name}
    return JSONResponse(status_code=404, content={"error": "Voice not found"})
