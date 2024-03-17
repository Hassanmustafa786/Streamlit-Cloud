from openai import OpenAI
import streamlit as st
from audio_recorder_streamlit import audio_recorder
from dotenv import load_dotenv
import io
import os

load_dotenv()

def transcribe(audio_bytes):
    if audio_bytes:
        audio_bytes_io = io.BytesIO(audio_bytes)
        # Convert the BytesIO object to a temporary file
        temp_file_path = "temp_audio.wav"  # Assuming the audio is in WAV format
        with open(temp_file_path, "wb") as temp_file:
            temp_file.write(audio_bytes_io.read())
            
        # Initialize the OpenAI client
        client = OpenAI()
        # Create transcription
        with open(temp_file_path, "rb") as audio_file:
            transcription = client.audio.transcriptions.create(
                model="whisper-1", 
                file=audio_file
            )
            
        # Remove the temporary file
        os.remove(temp_file_path)
        
        # Return the transcription text
        return transcription.text

audio_bytes = audio_recorder(key=f"Q1",
                                icon_size="2x",
                                text="Click to answer")
# if audio_bytes:
#     # Convert audio_bytes to a BytesIO object
#     audio_bytes_io = io.BytesIO(audio_bytes)

#     # Convert the BytesIO object to a temporary file
#     temp_file_path = "temp_audio.wav"  # Assuming the audio is in WAV format
#     with open(temp_file_path, "wb") as temp_file:
#         temp_file.write(audio_bytes_io.read())

#     # Transcribe the audio
#     text = transcribe(temp_file_path)

#     # Display the transcription
#     st.write(text)

#     # Optionally, remove the temporary file
#     os.remove(temp_file_path)
if audio_bytes:
    text = transcribe(audio_bytes)
    st.write(text)
