import streamlit as st
import os
import time
from deep_translator import GoogleTranslator
from audio_recorder_streamlit import audio_recorder
from streamlit_mic_recorder import mic_recorder,speech_to_text
import uuid
import io
from gtts import gTTS
import speech_recognition as sr
from openai import OpenAI
from dotenv import load_dotenv
from itertools import zip_longest
from streamlit_chat import message
from langchain_openai import ChatOpenAI
from langchain.schema import SystemMessage, HumanMessage, AIMessage
from operator import itemgetter
from langchain.memory import ConversationBufferMemory
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import RunnableLambda, RunnablePassthrough
import webbrowser

st.set_page_config(
    page_title="ICNA App",
    page_icon="🗣",
    layout="wide",
)
st.header('Translator', divider='orange')

def recognize_audio(audio_bytes, lang):
    query = ""  
    if audio_bytes:
        # st.audio(audio_bytes, format="audio/wav")
        r = sr.Recognizer()
        try:
            with io.BytesIO(audio_bytes) as wav_io:
                with sr.AudioFile(wav_io) as source:
                    audio_data = r.record(source)
                    query = r.recognize_google(audio_data, language= lang)  # Change the language code if needed
                    # st.warning(f"You: {query}\n")
        except sr.UnknownValueError:
            st.error("Google Speech Recognition could not understand audio.")
        except sr.RequestError as e:
            st.error(f"Could not request results from Google Speech Recognition service; {e}")
    
    return query

# def display_languages(languages):
#         st.subheader("Language Names")
#         language_names = [lang[0] for lang in languages]
#         st.write(language_names)
        
dic = [
        ('english', 'en', 'en-EN'),
        ('arabic', 'ar', 'ar-SA'),
        ('bengali', 'bn', 'bn-BD'),
        ('french', 'fr', 'fr-FR'),
        ('german', 'de', 'de-DE'),
        ('gujarati', 'gu', 'gu-IN'),
        ('hindi', 'hi', 'hi-IN'),
        ('italian', 'it', 'it-IT'),
        ('japanese', 'ja', 'ja-JP'),
        ('korean', 'ko', 'ko-KR'),
        ('malayalam', 'ml', 'ml-IN'),
        ('marathi', 'mr', 'mr-IN'),
        ('nepali', 'ne', 'ne-NP'),
        ('russian', 'ru', 'ru-RU'),
        ('spanish', 'es', 'es-ES'),
        ('tamil', 'ta', 'ta-IN'),
        ('urdu', 'ur', 'ur-UR')
    ]

def bolo(question, lang):
    speech = gTTS(text=question, lang=lang, slow=False, tld="co.in")
    key = str(uuid.uuid4())
    filename = f'pages/Languages/{lang+"_"+key}.mp3'
    speech.save(filename)
    with st.spinner('Wait for it...'):
        time.sleep(2)
    return st.audio(f'pages/Languages/{lang+"_"+key}.mp3')

os.makedirs('pages/Languages', exist_ok=True)

def translator():
    # display_languages(dic)

    # Display selected language code
    col1, col2 = st.columns(2)
    
    with col1:
        selected_language = st.selectbox("Select source language", [lang[0] for lang in dic], key="source")
        selected_language_code = [lang[1] for lang in dic if lang[0] == selected_language][0]
        selected_language_code_with_country = [lang[2] for lang in dic if lang[0] == selected_language][0]
        
        audio_bytes = audio_recorder(key= "Translate",
                                    icon_size="2x")
        # st.write(selected_language_code)
        # st.write(selected_language_code_with_country)
        # st.caption("Complete voice message in 10 secs")
        if audio_bytes:
            st.audio(audio_bytes, format="audio/mp3")
            # st.caption("Source voice")
            r = sr.Recognizer()
            try:
                with io.BytesIO(audio_bytes) as wav_io:
                    with sr.AudioFile(wav_io) as source:
                        audio_data = r.record(source)
                        query = r.recognize_google(audio_data, language = selected_language_code_with_country)  # Change the language code if needed
                        st.success(f"You: {query}\n")
            except sr.UnknownValueError:
                st.error("Google Speech Recognition could not understand audio.")
            except sr.RequestError as e:
                st.error(f"Could not request results from Google Speech Recognition service; {e}")

    with col2:
        selected_language = st.selectbox("Select source language", [lang[0] for lang in dic], key="convert")
        selected_language_code = [lang[1] for lang in dic if lang[0] == selected_language][0]
        selected_language_code_with_country = [lang[2] for lang in dic if lang[0] == selected_language][0]
        
        if 'query' in locals():
            translated = GoogleTranslator(source='auto', target=f'{selected_language}').translate(query)
            st.warning("Translating...")

            # Generate the audio
            audio = bolo(translated, selected_language_code)
            # st.caption("Target Voice")
            st.success(f"Translate: {translated}")
            
            
if __name__ == "__main__":
    translator()