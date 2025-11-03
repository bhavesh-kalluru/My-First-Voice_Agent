# 🎙️ Voice Agent (Streamlit UI)

A minimal voice agent that:
1) captures audio from your mic,
2) uses Google STT via `SpeechRecognition` to get text,
3) sends it to OpenAI GPT-4o for a reply,
4) streams TTS back via `gpt-4o-mini-tts`,
5) and plays the audio locally.

This repo contains:
- `app_streamlit.py` — Streamlit UI
- Your original Python logic/clients, preserved in the same form (imports, `tts()`, prompt, and message flow).

## Requirements

- Python 3.10–3.12 recommended (3.13 works but some libs lag behind).
- macOS users: PortAudio is required for PyAudio.

### Install

```bash
# Create and activate a venv (recommended)
python -m venv .venv
source .venv/bin/activate  # macOS/Linux
# .venv\Scripts\activate   # Windows

pip install --upgrade pip

# Core deps
pip install streamlit SpeechRecognition openai python-dotenv

# Audio I/O (PyAudio depends on PortAudio)
# macOS:
brew install portaudio
pip install pyaudio

# Windows:
# pip install pipwin
# pipwin install pyaudio

# Linux (Debian/Ubuntu):
# sudo apt-get install portaudio19-dev python3-dev
# pip install pyaudio
Create a .env file in the project root:

ini
Copy code
OPENAI_API_KEY=sk-...
Run
bash
Copy code
streamlit run app_streamlit.py
Open the local URL shown by Streamlit.

Using the App
In the left sidebar, set device_index to your real mic.

From prior probing, your MacBook Air Microphone was index 1.

Click “🎤 Speak now”.

Wait for “Listening…”, speak a short sentence.

The transcript appears, GPT responds, and speech plays back.

Troubleshooting
No audio captured / times out

System Settings → Privacy & Security → Microphone → allow your Terminal/IDE.

System Settings → Sound → Input → select the correct mic; check the level meter.

Try a different sample_rate (e.g., 44100).

BlackHole or virtual device is default

Set your physical mic as default in macOS Sound settings, or set device_index in the sidebar.

PyAudio build issues

macOS: brew install portaudio then pip install pyaudio.

Windows: pip install pipwin then pipwin install pyaudio.

Notes
This app performs one interaction per click, which is the Streamlit-friendly equivalent of your console while True loop. The underlying prompt, model, and conversation state are unchanged (messages stored in st.session_state.messages).

TTS uses gpt-4o-mini-tts with voice="coral" and streams audio via LocalAudioPlayer.
