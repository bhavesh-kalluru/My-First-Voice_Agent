## CHATGPT###
# ---------------------------------------------
# app_streamlit.py
# ---------------------------------------------

# Import standard libraries used in your original script
import os  # used to access environment variables like OPENAI_API_KEY
import asyncio  # used to run the async TTS function from a sync context

# Third-party libraries (same as your code)
import speech_recognition as sr  # SpeechRecognition for mic -> text
from dotenv import load_dotenv  # load .env variables from file

# OpenAI SDKs (same as your code)
from openai import OpenAI  # sync client for Chat Completions
from openai import AsyncOpenAI  # async client for streaming TTS
from openai.helpers import LocalAudioPlayer  # helper to play streamed audio locally

# Streamlit for the UI
import streamlit as st  # Streamlit creates the web UI

# ---------------------------------------------
# Environment + clients (unchanged from your code)
# ---------------------------------------------
load_dotenv()  # load environment variables from a .env file in the project root

client = OpenAI()        # create the sync OpenAI client for chat completions
async_client = AsyncOpenAI()  # create the async OpenAI client for streaming TTS

# ---------------------------------------------
# Async TTS function (unchanged core, just moved here)
# ---------------------------------------------
async def tts(speech_text: str):  # same param name and behavior you settled on
    """
    Stream TTS audio and play it locally.
    Uses the official streaming context manager.
    """
    # NOTE: same model/voice/format you used
    async with async_client.audio.speech.with_streaming_response.create(
        model="gpt-4o-mini-tts",  # TTS model
        voice="coral",            # voice preset
        input=speech_text,        # text to speak
        response_format="wav",    # streamed audio format
    ) as resp:
        # play audio chunks as they arrive
        await LocalAudioPlayer().play(resp)

# ---------------------------------------------
# System prompt (unchanged, same intention)
# ---------------------------------------------
SYSTEM_PROMPT = (
    "You are an expert in voice agent. "
    "you are given the transcript of what user said using voice. "
    "you need to output as if you are an voice agent what ever you speak will be converted "
    "back to audio as ai and play back to user"
)

# ---------------------------------------------
# Streamlit page config + title
# ---------------------------------------------
st.set_page_config(page_title="Voice Agent UI", page_icon="🎙️")  # page metadata for browser tab
st.title("🎙️ Voice Agent (Streamlit)")  # big page title

# ---------------------------------------------
# Session state for persistent conversation (same messages list concept)
# ---------------------------------------------
if "messages" not in st.session_state:  # create once per browser session
    st.session_state.messages = [{"role": "system", "content": SYSTEM_PROMPT}]  # seed with your system prompt

# ---------------------------------------------
# Controls & status area
# ---------------------------------------------
st.write("Click the button below and speak when prompted. The agent will reply and read it back.")

# Optional toggles for debugging / comfort
use_device_index = st.sidebar.number_input(
    "Mic device_index (MacBook Air Microphone was 1 in your probe)",
    min_value=0, value=1, step=1
)  # keep the same device index choice you used (1)
sample_rate = st.sidebar.selectbox("Sample rate", [16000, 44100], index=0)  # same rates you tried before
chunk_size = st.sidebar.selectbox("Chunk size", [1024, 2048], index=0)  # consistent with your previous settings
pause_threshold = st.sidebar.slider("Pause threshold (sec)", 0.5, 3.0, 2.0, 0.1)  # same 2s default

# A text area to show/keep the transcript history (optional UI, not changing core logic)
with st.expander("Conversation (running context)"):
    for m in st.session_state.messages:
        if m["role"] != "system":
            st.markdown(f"**{m['role'].capitalize()}:** {m['content']}")

# ---------------------------------------------
# One-turn interaction button (replaces while True for Streamlit)
# ---------------------------------------------
if st.button("🎤 Speak now"):
    # We keep the same SpeechRecognition pattern as your code,
    # just scoped to the button press so Streamlit doesn't hang.
    r = sr.Recognizer()  # recognizer instance for STT
    r.dynamic_energy_threshold = True  # adaptive energy threshold
    r.pause_threshold = pause_threshold  # same behavior you used

    # Provide immediate UI feedback
    st.info("Calibrating mic… start speaking after the beep/ready message.")
    st.write("(If nothing happens, check macOS permissions and your device_index.)")

    # Try mic capture and STT in a safe block, as your code does
    try:
        with sr.Microphone(device_index=use_device_index, sample_rate=sample_rate, chunk_size=chunk_size) as source:
            r.adjust_for_ambient_noise(source, duration=0.8)  # brief calibration (you used default earlier)
            st.success("Listening… (you have ~10 seconds to start)")
            # Keep your blocking listen pattern similar to the original
            audio = r.listen(source, timeout=10, phrase_time_limit=20)  # start within 10s, max 20s phrase
    except sr.WaitTimeoutError:
        st.error("No speech detected—try again, check mic selection/permissions, or speak sooner.")
    except Exception as e:
        st.error(f"Microphone error: {e}")
    else:
        # Try Google STT (same as your code)
        try:
            stt_text = r.recognize_google(audio)  # transcribe
            st.write(f"**You said:** {stt_text}")  # display to UI
        except sr.UnknownValueError:
            st.warning("Sorry, I couldn’t understand the audio.")
            stt_text = None
        except sr.RequestError as e:
            st.error(f"Speech service error: {e}")
            stt_text = None

        if stt_text:
            # Append user message to the running context (same as your code)
            st.session_state.messages.append({"role": "user", "content": stt_text})

            # Call Chat Completions with your same model and messages list
            try:
                chat_resp = client.chat.completions.create(
                    model="gpt-4o",
                    messages=st.session_state.messages
                )
                ai_text = chat_resp.choices[0].message.content  # extract reply text
                st.session_state.messages.append({"role": "assistant", "content": ai_text})  # keep history

                # Show in UI (same content you print)
                st.success("**AI Response:**")
                st.write(ai_text)

                # Speak it (your same TTS function)
                with st.spinner("Speaking…"):
                    asyncio.run(tts(ai_text))
            except Exception as e:
                st.error(f"OpenAI error: {e}")

# ---------------------------------------------
# Footer note
# ---------------------------------------------
st.caption("Tip: If your Mac has 'BlackHole' or other virtual devices, set the correct device_index in the sidebar.")


"""🎚️ 1. Sample Rate = 16 000 Hz (16 kHz)

Why 16 kHz is the “sweet spot” for speech:

Human speech bandwidth is ~ 0–8 kHz; Nyquist says you need at least double that → 16 kHz.
Google SpeechRecognition API and many STT/TTS models (OpenAI, Whisper, etc.) are optimized for 16 kHz mono audio.
Higher rates (e.g. 44.1 kHz / 48 kHz) make no difference for voice quality but triple the data throughput.
Lower rates (8 kHz) lose intelligibility, especially for consonants.

👉 So 16 kHz = efficient, high-accuracy speech recognition standard.




⚙️ 2. Chunk Size = 1024 Frames
A “chunk” is how many audio frames PyAudio reads per block.
Latency vs. CPU:
Small chunk (512 / 256) → lower latency but more callbacks → higher CPU.
Large chunk (2048 / 4096) → higher latency but fewer callbacks → smoother for long recordings.
SpeechRecognition default is 1024 frames ≈ 64 ms (16 000 / 1024 ≈ 15.6 blocks per second).
That’s fast enough for speech, low enough CPU overhead, and fully supported by PortAudio.

👉 1024 frames @ 16 kHz ≈ 64 ms latency → natural response timing without overloading your laptop."""