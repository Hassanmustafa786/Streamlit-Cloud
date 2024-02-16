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

os.makedirs('Questions/English', exist_ok=True)
os.makedirs('Questions/Urdu', exist_ok=True)
os.makedirs('Questions/Spanish', exist_ok=True)
os.makedirs('Questions/Bengali', exist_ok=True)
os.makedirs('Questions/Arabic', exist_ok=True)

os.makedirs('Answers/English', exist_ok=True)
os.makedirs('Answers/Urdu', exist_ok=True)
os.makedirs('Answers/Spanish', exist_ok=True)
os.makedirs('Answers/Bengali', exist_ok=True)
os.makedirs('Answers/Arabic', exist_ok=True)


def speak(question, key, lang):
    if lang == 'en':
        folder_name = 'Questions/English'
    elif lang == 'es':
        folder_name = 'Questions/Spanish'
    elif lang == 'ur': 
        folder_name = 'Questions/Urdu'
    elif lang == 'bn': 
        folder_name = 'Questions/Bengali'
    elif lang == 'ar': 
        folder_name = 'Questions/Arabic'
    
    filename = f'{folder_name}/Q{key}.mp3'
    if not os.path.exists(filename):
        speech = gTTS(text=question, lang=lang, slow=False, tld="co.in")
        speech.save(filename)
    st.audio(filename)

def text_to_speech(answer, key, lang):
    speech = gTTS(text=answer, lang=lang, slow=False, tld="co.in")
    if lang == 'en':
        filename = f'Answers/English/A{key}.mp3'
        speech.save(filename)
    elif lang == 'ur':
        filename = f'Answers/Urdu/A{key}.mp3'
        speech.save(filename)
    elif lang == 'es':
        filename = f'Answers/Spanish/A{key}.mp3'
        speech.save(filename)
    elif lang == 'bn':
        filename = f'Answers/Bengali/A{key}.mp3'
        speech.save(filename)
    elif lang == 'ar':
        filename = f'Answers/Arabic/A{key}.mp3'
        speech.save(filename)
    st.audio(filename)

# load_dotenv()
# openai_api_key = os.getenv("OPENAI_API_KEY")
chat = ChatOpenAI(
    temperature=0.5,
    model_name="gpt-3.5-turbo",
    openai_api_key= st.secrets["OPENAI_API_KEY"],
    max_tokens=100,
)

questions = [
    ("What is your name?", 1, "آپ کا نام کيا ہے?", "¿Cómo te llamas?", "আপনার নাম কি?", "ما اسمك؟"),
    ("What is your age?", 2, "آپ کی عمر کیا ہے؟", "¿Cuántos años tienes?", "আপনার বয়স কত?", "ما هو عمرك؟"),
    ("What is your address?", 3, "آپ کا پتہ کیا ہے؟", "¿Cuál es su dirección?", "আপনার ঠিকানা কি?", "ما هو عنوانك؟"),
    ("Are you taking any Medications? If yes, then please tell name of the medication.", 4, "کیا آپ کوئی دوا لے رہے ہیں؟اگر ہاں. پھر دوا کا نام بتائیں ", "¿Está tomando algún medicamento? En caso afirmativo, indique el nombre del medicamento.", "আপনি কি কোনো ওষুধ খাচ্ছেন? যদি হ্যাঁ, তাহলে ওষুধের নাম বলুন।", "هل أنت مع أي أدوية؟ إذا كانت الإجابة بنعم، يرجى ذكر اسم الدواء."),
    ("Can you name the medicines?", 5, "کیا آپ ادویات کے نام بتا سکتے ہیں؟ ", "¿Puedes nombrar los medicamentos?", "ওষুধের নাম বলতে পারবেন?", "هل يمكنك تسمية الأدوية؟"),
    ("What other medicine have you taken in the past?", 6, "آپ نے ماضی میں اور کون سی دوا لی ہے؟ ", "¿Qué otro medicamento ha tomado en el pasado?", "অতীতে আপনি অন্য কোন ওষুধ খেয়েছেন?", "ما هي الأدوية الأخرى التي تناولتها في الماضي؟"),
    ("What is your major complaint?", 7, "آپ کی سب سے بڑی شکایت کیا ہے؟ ", "¿Cuál es su principal queja?", "আপনার প্রধান অভিযোগ কি?", "ما هي شكواك الرئيسية؟"),
    ("Have you previously suffered from this complaint?", 8, "کیا آپ کو پہلے بھی اس شکایت کا سامنا کرنا پڑا ہے؟", "¿Ha sufrido anteriormente esta dolencia?", "আপনি কি আগে এই অভিযোগ থেকে ভুগছেন?", "هل عانيت من قبل من هذه الشكوى؟"),
    ("What previous therapists have you seen?", 9, "آپ نے پچھلے کون سے تھراپسٹ کو دیکھا ہے؟", "¿A qué terapeuta has visto anteriormente?", "আপনি কি আগের থেরাপিস্ট দেখেছেন?", "ما المعالجين السابقين الذين رأيتهم؟"),
    ("Can you describe the treatment?", 10, "کیا آپ علاج کی وضاحت کر سکتے ہیں؟", "¿Puede describir el tratamiento?", "আপনি চিকিত্সা বর্ণনা করতে পারেন?", "هل يمكنك وصف العلاج؟"),
    ("What is your family history?", 11, "کیا آپ مجھے اپنے خاندان کی تاریخ کے بارے میں بتا سکتے ہیں؟", "¿Cuál es su historia familiar?", "আপনার পারিবারিক ইতিহাস কি?", "ما هو تاريخ عائلتك؟"),
    ("Are you adopted?", 12, "کیا آپ کو گود لیا گیا تھا؟", "¿Eres adoptado?", "আপনি কি দত্তক?", "هل أنت متبنى؟"),
    ("If yes, at what age were you adopted?", 13, "اگر ہاں، تو آپ کو کس عمر میں گود لیا گیا تھا؟", "En caso afirmativo, ¿a qué edad fue adoptado?", "যদি হ্যাঁ, কোন বয়সে আপনাকে দত্তক নেওয়া হয়েছিল?", "إذا كانت الإجابة بنعم، في أي عمر تم تبنيك؟"),
    ("How is your relationship with your mother?", 14, "ماں کے ساتھ آپ کا رشتہ کیسا ہے؟", "¿Cómo es tu relación con tu madre?", "আপনার মায়ের সাথে আপনার সম্পর্ক কেমন?", "كيف هي علاقتك مع والدتك؟"),
    ("Where did you grow up?", 15, "آپ کہاں بڑے ہوئے؟", "¿Dónde creciste?", "আপনি কোথায় বড় হয়েছেন?", "أين نشأت؟"),
    ("Are you married?", 16, "کيا آپ شادی شدہ ہيں", "¿Estás casado?", "আপনি কি বিবাহিত?", "هل أنت متزوج؟"),
    ("If yes, specify the date of marriage?", 17, "اگر ہاں، تو شادی کی تاریخ بتائیں؟", "En caso afirmativo, especifique la fecha del matrimonio.", "যদি হ্যাঁ, বিয়ের তারিখ উল্লেখ করবেন?", "إذا كانت الإجابة بنعم، حدد تاريخ الزواج؟"),
    ("Do you have children?", 18, "کیا آپ کے بچے ہیں؟", "¿Tienes hijos?", "আপনার কি সন্তান আছে?", "هل لديك أطفال؟"),
    ("If yes, how is your relationship with your children?", 19, "کیا آپ کے بچے ہیں؟", "En caso afirmativo, ¿cómo es su relación con sus hijos?", "যদি হ্যাঁ, আপনার সন্তানদের সাথে আপনার সম্পর্ক কেমন?", "إذا نعم كيف هي علاقتك مع أطفالك؟"),
]

def generate_audio():
    for i, (en_question, key, ur_question, es_question, bn_question, ar_question) in enumerate(questions):
        if selected_language == 'en':
            speak(en_question, key, selected_language)
        elif selected_language == 'ur':
            speak(ur_question, key, selected_language)
        elif selected_language == 'es':
            speak(es_question, key, selected_language)
        elif selected_language == 'bn':
            speak(bn_question, key, selected_language)
        elif selected_language == 'ar':
            speak(ar_question, key, selected_language)

def intro():
    if selected_language == 'en':
        speak("Welcome to ICNA-Relief","0", 'en')
    elif selected_language == 'ur':
        speak("آئی سی این اے ریلیف میں خوش آمدید. شکریہ", '0', 'ur')
    elif selected_language == 'es':
        speak("Bienvenidos a ICNA-Relief", '0', 'es')
    elif selected_language == 'bn':
        speak("ICNA-রিলিফে স্বাগতম", '0', 'bn')
    elif selected_language == 'ar':
        speak("مرحبا بكم في إغاثة ICNA", '0', 'ar')

st.set_page_config(
    page_title="OSTF App",
    page_icon="🧊",
    layout="wide",
)

st.header('Health Intake Questionnaire', divider='orange')
st.markdown('''Welcome To! I C N A - Releif Organization''')
selected_language = st.sidebar.selectbox("Select Language", ["en", "ur", "es", "bn", "ar"])
tab1, tab2 = st.tabs(["Q & A", "Translator"])

# Initialize session state variable
if 'chat_history' not in st.session_state:
    st.session_state['chat_history'] = []

if 'generated' not in st.session_state:
    st.session_state['generated'] = []

if 'past' not in st.session_state:
    st.session_state['past'] = []  # Store past user inputs

# Define a function to generate response
def generate_response(user_query):
    # Build the list of messages
    zipped_messages = build_message_list(user_query)

    # Generate response using the chat model
    ai_response = chat(zipped_messages)
    response = ai_response.content
    return response

# Define a function to build a message list
def build_message_list(user_query):
    """
    Build a list of messages including system, human, and AI messages.
    """
    # Start zipped_messages with the SystemMessage
    zipped_messages = [SystemMessage(
        content= """You are a Health Care Expert for ICNA Relief, here to guide and assist people with their health questions and concerns. Please provide accurate and helpful information, and always maintain a polite and professional tone.
                    Your answer should be complete and precise.
                    If a user tell his/her name, age, address then just thank him and end the chat.
                    If a user tell his/her about personal life then just thank him and end the chat.
                    You have to answer briefly only health related questions.
                    You understand only these languages urdu, english, spanish, arabic and bengali.
                    If a user talk with different language which is not given then tell him I cannot understand your language."""
    )]

    # Zip together the past and generated messages
    for human_msg, ai_msg in zip_longest(st.session_state['past'], st.session_state['generated']):
        if human_msg is not None:
            zipped_messages.append(HumanMessage(
                content=human_msg))  # Add user messages
        if ai_msg is not None:
            zipped_messages.append(
                AIMessage(content=ai_msg))  # Add AI messages

    zipped_messages.append(HumanMessage(content=user_query))  # Add the latest user message

    return zipped_messages

user_input = ""

# Define a function to display the conversation history for text input in newest to oldest order
def display_text_conversation_history():
    for i in range(len(st.session_state['generated']) - 1, -1, -1):
        if i < len(st.session_state["past"]):
            message(st.session_state["past"][i], is_user=True, key=str(i) + '-text-user')
        message(st.session_state["generated"][i], key=str(i) + '-text')

# Define a function to display the conversation history for audio input in newest to oldest order
def display_audio_conversation_history():
    for i in range(len(st.session_state['generated']) - 1, -1, -1):
        if i < len(st.session_state["past"]):
            message(st.session_state["past"][i], is_user=True, key=str(i) + '-audio-user', avatar_style='lorelei')
        message(st.session_state["generated"][i], key=str(i) + '-audio', avatar_style='bottts')

if 'question_number' not in st.session_state:
    st.session_state.question_number = 1

# Create a sidebar
with st.sidebar:
    st.write("Introduction:")
    intro()
    # generate_audio()

# Display audio conversation history in the sidebar
with st.sidebar.expander("Conversation History"):
    display_audio_conversation_history()

with tab1:
    st.write(f"Question: {st.session_state.question_number}")
    speak(questions, st.session_state.question_number, selected_language)
    audio_bytes = audio_recorder(key=f"Q{st.session_state.question_number}",
                                 icon_size="2x")
    
    if selected_language == 'en':
        user_input = recognize_audio(audio_bytes, "en-EN")
    elif selected_language == 'ur':
        user_input = recognize_audio(audio_bytes, "ur-UR")
    elif selected_language == 'es':
        user_input = recognize_audio(audio_bytes, "es-ES")
    elif selected_language == 'bn':
        user_input = recognize_audio(audio_bytes, "bn-BD")
    elif selected_language == 'ar':
        user_input = recognize_audio(audio_bytes, "ar-SA")
    
    # Trigger a rerun to update the UI
    if st.button("Next Question ▶️", key=f"{selected_language}"):
        st.session_state.question_number += 1
        st.rerun()
    
    # st.divider()
    if user_input:
        # Append user query to past queries
        st.session_state.past.append(user_input)

        # Generate response
        output = generate_response(user_input)

        # Append AI response to generated responses
        st.session_state.generated.append(output)
        # User input
        st.markdown(f'<div class="chat-bubble user" id="bot-message">🤵🏻: {user_input}</div>', unsafe_allow_html=True)
        # Bot output
        st.markdown(f'<div class="chat-bubble bot" id="bot-message">🤖: {output}</div>', unsafe_allow_html=True)

        # Custom CSS
        st.markdown('''
            <style>
                .chat-bubble {
                    font-size: large;
                    color: white;
                    padding: 10px;
                    border-radius: 10px;
                    margin: 10px 0;
                    transition: background-color 0.3s;
                    cursor: pointer;
                    word-wrap: break-word;
                }

                .user {
                    background-color: #F36D1F;
                    overflow: hidden;
                    white-space: wrap;
                    width: 0;
                    animation: typing 1s steps(30, end) forwards;
                }

                .bot {
                    background-color: black;
                    overflow: hidden;
                    white-space: wrap;
                    width: 0;
                    animation: typing 1s steps(30, end) forwards;
                }

                .chat-bubble:hover {
                    background-color: #555;
                }

                @keyframes typing {
                    from {
                        width: 0;
                    }
                    to {
                        width: 100%;
                    }
                }
            </style>
        ''', unsafe_allow_html=True)

        # Custom JavaScript
        st.markdown('''
            <script>
                setTimeout(function() {
                    document.getElementById('bot-message').innerHTML += ' {message}';
                }, 2000);
            </script>
        ''', unsafe_allow_html=True)
        text_to_speech(output, st.session_state.question_number, selected_language)

    else:
        if selected_language == 'en':
            if 'en' != selected_language:
                st.warning("Please select the language first.")
        elif selected_language == 'ur':
            if 'ur' != selected_language:
                st.warning("براہ مہربانی دوسرے سوال کی طرف جائیں۔")
        elif selected_language == 'es':
            if 'es' != selected_language:
                st.warning("Por favor, seleccione el idioma primero.")
        elif selected_language == 'bn':
            if 'bn' != selected_language:
                st.warning("প্রথমে ভাষা নির্বাচন করুন.")
        elif selected_language == 'ar':
            if 'ar' != selected_language:
                st.warning("الرجاء تحديد اللغة أولا.")
            
            
#------------------------------------------------------------------------------------
def display_languages(languages):
    st.subheader("Language Names")

    # Extract language names from the list of tuples
    language_names = [lang[0] for lang in languages]
    st.write(language_names)
    
dic = [
    ('arabic', 'ar', 'ar-SA'),
    ('bengali', 'bn', 'bn-BD'),
    ('english', 'en', 'en-EN'),
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
    filename = f'Languages/{lang+"_"+key}.mp3'
    speech.save(filename)
    with st.spinner('Wait for it...'):
        time.sleep(2)
    return st.audio(f'Languages/{lang+"_"+key}.mp3')

# Make a folder
os.makedirs('Languages', exist_ok=True)

with tab2:
    display_languages(dic)

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
    