# PDF-to-Audiobook API 🎧📄

Convert PDFs into AI-generated or cloned-voice audiobooks using **FastAPI**, **OpenVoice**, and automation with **n8n**. Fully self-hostable on Windows with Nginx and persistent services.

---

## **Features**

- Upload PDF and preview extracted text
- Generate audiobook with:
  - AI voice  
  - Your own cloned voice (WAV sample)
- Download generated audiobook in **MP3** or **WAV**
- Manage voice samples (upload, list, delete)
- List previously generated audiobooks
- Health check endpoint for monitoring
- Fully automatable workflow via **n8n**

---

## **Tech Stack**

- **Backend:** Python 3.9+, FastAPI, Uvicorn
- **TTS Engine:** OpenVoice AI / Custom Voice Cloning
- **Audio Processing:** FFmpeg, Pydub
- **Frontend:** HTML + JavaScript (served via FastAPI)
- **Workflow Automation:** n8n
- **Production:** Nginx reverse proxy, NSSM service (Windows)
- **Logging:** RotatingFileHandler

---

## **Directory Structure**

```
PDFToAudiobook/
│
├─ book_texts/          # PDF text storage
├─ audio_output/        # Generated audiobooks
├─ audio_chunks/        # Temporary chunks for cloned voice
├─ myVoice/             # Uploaded voice samples
├─ logs/                # Server logs
├─ main.py              # FastAPI app
├─ extract_pdf_text.py
├─ convert_to_aiVoice.py
├─ convert_to_myVoice.py
├─ merge_audio.py
```

---

## **Setup Instructions**

### **1. System Requirements**

- 8GB+ RAM, 4+ CPU cores (GPU optional for faster TTS)
- Python 3.9 or 3.10
- Git, FFmpeg
- CUDA toolkit (optional)

---

### **2. Project Setup**

```powershell
# Clone project
git clone https://github.com/ibraheem8887/AudioBook-n8n.git
cd pdf-to-audiobook

# Create virtual environment
python -m venv venv
.\venv\Scripts\activate



---

### **3. OpenVoice Setup**

```powershell
git clone https://github.com/openvoice/openvoice.git
cd openvoice
pip install -e .
```

- Download V1 and V2 model checkpoints
- Test basic TTS functionality

---

### **4. Run FastAPI (Development)**

```powershell
uvicorn main:app --host 127.0.0.1 --port 8000 --reload
```

- Open browser: [http://localhost:8000](http://localhost:8000)
- Upload PDF, preview text, select voice, generate audiobook

---

### **5. Production Deployment (Windows)**

#### **Nginx Reverse Proxy**

- Download Nginx for Windows: [https://nginx.org/en/download.html](https://nginx.org/en/download.html)
- Configure `nginx.conf`:

```nginx
server {
    listen 80;
    server_name localhost;

    location / {
        proxy_pass http://127.0.0.1:8000;
    }

    location /audio/ {
        alias C:/PDFToAudiobook/audio_output/;
    }

    location /voice_samples/ {
        alias C:/PDFToAudiobook/myVoice/;
    }
}
```

- Start Nginx: `start nginx.exe` in PowerShell

---

#### **Persistent Service (NSSM)**

- Download NSSM: [https://nssm.cc/download](https://nssm.cc/download)
- Install FastAPI as a Windows service:

```powershell
C:\nssm-2.24\win64\nssm.exe install OpenVoiceAPI
# Path: C:\PDFToAudiobook\venv\Scripts\python.exe
# Arguments: -m uvicorn main:app --host 127.0.0.1 --port 8000 --workers 4 --log-level info
# Startup directory: C:\PDFToAudiobook
```

- Start the service:

```powershell
C:\nssm-2.24\win64\nssm.exe start OpenVoiceAPI
```

---

### **6. n8n Automation**

- Install n8n:

```powershell
npm install n8n -g
n8n
```

- Open workflow editor: [http://localhost:5678](http://localhost:5678)
- Example workflow:
  - **HTTP Request** → Upload PDF
  - **Call FastAPI /extract_pdf_preview**
  - **Call /tts** with voice selection
  - **Notify via Slack or email** with audiobook URL

---

## **API Endpoints**

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Home page (PDF upload + TTS UI) |
| `/health` | GET | Check directory & service health |
| `/extract_pdf_preview` | POST | Upload PDF → extract preview text |
| `/tts` | POST | Generate audiobook (AI or myVoice) |
| `/list_audiobooks` | GET | List generated audiobooks |
| `/voices` | GET | List uploaded voice samples |
| `/voices/{voice_name}` | DELETE | Delete a voice sample |

---

## **Usage**

1. Upload PDF → preview text
2. Choose **AI Voice** or **MyVoice**
3. Select output format (MP3/WAV)
4. Generate audiobook
5. Download or play online via the `/audio/` URL

---

## **Logging**

- Server logs: `logs/server.log` (rotating, max 10MB, 5 backups)
- Nginx logs: `logs/access.log`, `logs/error.log`

---

## **Contributing**

Contributions are welcome! Please:

1. Fork the repository
2. Create a branch (`feature/my-feature`)
3. Commit your changes
4. Open a Pull Request

---



