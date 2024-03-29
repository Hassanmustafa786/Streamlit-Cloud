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

load_dotenv()
chat = ChatOpenAI(
    temperature=0.5,
    model_name="gpt-3.5-turbo",
    openai_api_key= st.secrets['OPENAI_API_KEY'],
    max_tokens=100,
)

questions = [
    # Dialogue 1
    ("What is your name?", 1, "آپ کا نام کيا ہے?", "¿Cómo te llamas?", "আপনার নাম কি?", "ما اسمك؟"),
    ("What is your age?", 2, "آپ کی عمر کیا ہے؟", "¿Cuántos años tienes?", "আপনার বয়স কত?", "ما هو عمرك؟"),
    # Dialogue 2
    ("Are you taking any Medications? If yes, then please tell name of the medicines.", 3, "کیا آپ کوئی دوا لے رہے ہیں؟اگر ہاں. پھر دوا کا نام بتائیں ", "¿Está tomando algún medicamento? En caso afirmativo, indique el nombre del medicamento.", "আপনি কি কোনো ওষুধ খাচ্ছেন? যদি হ্যাঁ, তাহলে ওষুধের নাম বলুন।", "هل أنت مع أي أدوية؟ إذا كانت الإجابة بنعم، يرجى ذكر اسم الدواء."),
    # Dialogue 3
    ("What is your major complaint?", 4, "آپ کی سب سے بڑی شکایت کیا ہے؟ ", "¿Cuál es su principal queja?", "আপনার প্রধান অভিযোগ কি?", "ما هي شكواك الرئيسية؟"),
    # Dialogue 4 (Relationships)
    ("Are you adopted? If yes, at what age were you adopted?", 5, "کیا آپ کو گود لیا گیا ہے؟ اگر ہاں، تو آپ کو کس عمر میں گود لیا گیا تھا؟", "¿Eres adoptado? En caso afirmativo, ¿a qué edad fue adoptado?", "আপনি কি দত্তক নিয়েছেন? যদি হ্যাঁ, কোন বয়সে আপনাকে দত্তক নেওয়া হয়েছিল?", "هل تم تبنيك؟ إذا كانت الإجابة بنعم ، في أي عمر تم تبنيك؟"),
    ("How is your relationship with your parents?", 6, "والدین کے ساتھ آپ کے تعلقات کیسے ہیں؟", "¿Cómo es tu relación con tus padres?", "বাবা-মায়ের সঙ্গে আপনার সম্পর্ক কেমন?", "كيف هي علاقتك مع والديك؟"),
    ("Are your parents married?", 7, "کیا آپ کے والدین شادی شدہ ہیں؟", "¿Tus padres están casados?", "তোমার বাবা-মা কি বিবাহিত?", "هل والداك متزوجان؟"),
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
                    Your response should be in the same language in which you will get the text.
                    If a user tell his/her name, age, address then just thank him and end the chat.
                    If a user tell his/her about personal life then just thank him and end the chat.
                    You have to answer briefly only health related questions.
                    You understand only these languages urdu, english, spanish, arabic and bengali.
                    If a user talk with different language which is not given then tell him I cannot understand your language.
                    
                    I want you to follow these examples:
                    Example 1:
                    Q- What is your name? 
                    A- hello I am abc
                    
                    Your response: Thank you abc for sharing your name. Kindly respond to the next question to help us know you better.
                    
                    Example 2:
                    Q- What is your age? 
                    A- I am 23 years old.
                    
                    Your response: Thanks, xyz, for providing your age. Please continue by answering the next question to enhance our understanding.
                    
                    Example 3:
                    Q- Are you married? 
                    A- No, I'm not.
                    
                    Your response: Thank you abc for sharing your personal details. These things is necessary for the treatment to understand the patients life. Please continue by answering the next question to enhance our understanding.
                    
                    Your focus should be on answer and generate response based in this.
                    You will get the lots of question and answer text like the above examples and you have to analyze the text and make sure patient don't get bored from you so your responses should be complete and try to collect more and more details from the patient.
                    I want your response to be faithful because patient is here to give the information about his life and you have to collect the information, calm him and give medical advises.
                    Do not add this in your response "If you have any health-related questions or concerns, feel free to ask." because patient is giving details and your response should close like this "To learn more about you, please proceed to the next question.".
                    """
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


# Dictionary to store language-specific content
language_content = {
    'en': {
        'button_text': "Create Form",
        'welcome_message': "Welcome To! I C N A - Relief Organization",
        'intro_title': "Introduction:",
        'copyright_notice': "&copy; 2024 ICNA Relief. All rights reserved.",
        'next_question': "Next Question",
        'audio_text': "Click to answer",
        'speech_recognition_language': "en-EN",
        'header': "Health Intake Questionnaire",
        'dialogue_completion': "Congratulations! You have successfully completed all the dialogues.",
        'dialogue_1': "1_Demographic",
        'dialogue_2': "2_Medication",
        'dialogue_3': "3_Health_Condition",
        'dialogue_4': "4_Relationships",
        'dialogue_5': "5_Feelings_&_Family",
        'dialogue_6': "6_Treatment",
        'dialogue_7': "7_Addiction",
        'dialogue_8': "8_Translator",
    },
    'ur': {
        'button_text': "فارم بنائیں",
        'welcome_message': "خوش آمدید! آئی سی این اے - امدادی تنظیم",
        'intro_title': ":تعارف",
        'copyright_notice': "&copy; 2024 آئی سی این اے ریلیف۔ تمام حقوق محفوظ ہیں.",
        'next_question': "اگلا سوال",
        'audio_text': "جواب دینے کے لیے کلک کریں",
        'speech_recognition_language': "ur-UR",
        'header': "صحت کے استعمال کا سوالنامہ",
        'dialogue_completion': "مبارک ہو! آپ نے کامیابی کے ساتھ تمام مکالمے مکمل کیے ہیں۔",
        'dialogue_1': "1_آبادیاتی",
        'dialogue_2': "2_ادویات",
        'dialogue_3': "3_صحت_کی_حالت",
        'dialogue_4': "4_تعلقات",
        'dialogue_5': "5_احساسات_اور_خاندان",
        'dialogue_6': "6_علاج",
        'dialogue_7': "7_لت",
        'dialogue_8': "8_مترجم",
    },
    'es': {
        'button_text': "Crear formulario",
        'welcome_message': "¡Bienvenidas a! I C N A - Organización de Socorro",
        'intro_title': "Introducción:",
        'copyright_notice': "&copy; 2024 ICNA Relief. Todos los derechos reservados.",
        'next_question': "Siguiente pregunta",
        'audio_text': "Haga clic para responder",
        'speech_recognition_language': "es-ES",
        'header': "Cuestionario de Ingesta de Salud",
        'dialogue_completion': "¡Felicidades! Has completado con éxito todos los diálogos.",
        'dialogue_1': "1_Demográfica",
        'dialogue_2': "2_Medicación",
        'dialogue_3': "3_Estado_de_salud",
        'dialogue_4': "4_Relaciones",
        'dialogue_5': "5_Sentimientos_y_familia",
        'dialogue_6': "6_Tratamiento",
        'dialogue_7': "7_Adicción",
        'dialogue_8': "8_Traductora",
    },
    'bn': {
        'button_text': "ফর্ম তৈরি করুন",
        'welcome_message': "স্বাগতম! আই সি এন এ - ত্রাণ সংস্থা",
        'intro_title': "ভূমিকা:",
        'copyright_notice': "&copy; 2024 আইসিএনএ ত্রাণ। সর্বস্বত্ব সংরক্ষিত।",
        'next_question': "পরবর্তী প্রশ্ন",
        'audio_text': "উত্তর দিতে ক্লিক করুন",
        'speech_recognition_language': "bn-BD",
        'header': "স্বাস্থ্য গ্রহণের প্রশ্নাবলী",
        'dialogue_completion': "অভিনন্দন! আপনি সবগুলো কথোপকথন সফলভাবে শেষ করেছেন।",
        'dialogue_1': "1_জনসংখ্যাতাত্ত্বিক",
        'dialogue_2': "2_ঔষধ",
        'dialogue_3': "3_স্বাস্থ্যের_অবস্থা",
        'dialogue_4': "4_সম্পর্ক",
        'dialogue_5': "5_অনুভূতি_ও_পরিবার",
        'dialogue_6': "6_চিকিত্সা",
        'dialogue_7': "7_আসক্তি",
        'dialogue_8': "8_অনুবাদক",
    },
    'ar': {
        'button_text': "إنشاء نموذج",
        'welcome_message': "مرحبا بكم في! I C N A - منظمة الإغاثة",
        'intro_title': "مقدمة:",
        'copyright_notice': "&copy; 2024 إغاثة ICNA. كل الحقوق محفوظة.",
        'next_question': "السؤال التالي",
        'audio_text': "انقر للإجابة",
        'speech_recognition_language': "ar-SA",
        'header': "استبيان المدخول الصحي",
        'dialogue_completion': "مبروك! لقد أكملت بنجاح جميع الحوارات.",
        'dialogue_1': "1_الديمغرافيه",
        'dialogue_2': "2_دواء",
        'dialogue_3': "3_الحالة_الصحية",
        'dialogue_4': "4_العلاقات",
        'dialogue_5': "5_المشاعر_والعائلة",
        'dialogue_6': "6_العلاج",
        'dialogue_7': "7_إدمان",
        'dialogue_8': "8_Translator",
    }
}

language_mapping = {
    "English": "en",
    "Urdu": "ur",
    "Spanish": "es",
    "Bangla": "bn",
    "Arabic": "ar"
}

with st.sidebar:
    language = st.selectbox("Select Language", ["English", "Urdu", "Spanish", "Bangla", "Arabic"])
    st.session_state['demographic'] = language
    st.session_state['medication'] = language
    st.session_state['health'] = language
    st.session_state['relation'] = language
    st.session_state['feeling'] = language
    st.session_state['treatment'] = language
    st.session_state['addiction'] = language
    selected_language = language_mapping[language]
    if st.button(language_content[selected_language]['button_text']):
        file_path = r"D:\OSTF\StreamlitCloud\Intake_form_filled.html"
        webbrowser.open("file://" + file_path, new=2)

    st.markdown(language_content[selected_language]['welcome_message'])
    
    st.write(language_content[selected_language]['intro_title'])
    intro()
    
    # Copyright notice
    st.markdown(f"""
        <div style="text-align: center; padding: 10px; background-color: #1D1D1D; color: #FFFFFF;">
            {language_content[selected_language]['copyright_notice']}
        </div>
    """, unsafe_allow_html=True)
    
    # generate_audio()
     
    # Display audio conversation history in the sidebar
    with st.expander("Conversation History"):
        display_audio_conversation_history()

st.header(language_content[selected_language]['header'], divider='orange')

# Function to get translated dialogue name
# def get_translated_dialogue(selected_language, dialogue_key):
#     return language_content[selected_language].get(dialogue_key, dialogue_key)

# Assuming file_names contains the list of file names in the "pages" folder
# file_names = ["1_Demographic.py", "2_Medication.py", "3_Health_Condition.py", "4_Relationships.py", "5_Feeling_&_Family.py", "6_Treatment.py", "7_Addiction.py", "8_Translator.py"]

# # Rename files based on the selected language
# for old_name in file_names:
#     # Extract dialogue number from the old file name
#     dialogue_number = old_name.split("_")[0]
#     # Get the translated dialogue name
#     translated_dialogue_name = get_translated_dialogue(selected_language.lower(), f"{dialogue_number}_{"_".join(old_name.split('_')[1:])}")
#     # Form the new file name
#     new_name = f"{dialogue_number}_{translated_dialogue_name}"
#     # Rename the file
#     os.rename(os.path.join("pages", old_name), os.path.join("pages", new_name))

def home(selected_language):
    if 'question_number' not in st.session_state:
        st.session_state.question_number = 1

    languages = ['en', 'key', 'ur', 'es', 'bn', 'ar']
    language_index = languages.index(selected_language)
    # st.write(selected_language)
    # st.subheader(language_index)
    
    # name = "My name is Hassan."
    # st.markdown(f'{questions[st.session_state.question_number - 1][language_index]}<br>{name}', unsafe_allow_html=True)
    # st.write(f'{questions[st.session_state.question_number - 1][language_index]}\n{name}')
    
    if st.button(f"{language_content[selected_language]['next_question']} ▶️", key=f"{selected_language}"):
        st.session_state.question_number += 1
        st.rerun()
    
    if st.session_state.question_number <= 7:
        st.info(f"{questions[st.session_state.question_number - 1][1]}- {questions[st.session_state.question_number - 1][language_index]}")
        speak(questions, st.session_state.question_number, selected_language)
        audio_bytes = audio_recorder(key=f"Q{st.session_state.question_number}",
                                    icon_size="2x",
                                    text=f"{language_content[selected_language]['audio_text']}")
        
        user_input = recognize_audio(audio_bytes, language_content[selected_language]['speech_recognition_language'])
        if user_input:
            st.session_state.past.append(user_input)
            combine = f'Q- {questions[st.session_state.question_number - 1][language_index]}' + '\n\n' + f'A- {user_input}'
            # st.write(combine)
            output = generate_response(combine)
            st.session_state.generated.append(output)
            
            st.markdown(f'<div class="chat-bubble user" id="bot-message">🤵🏻: {user_input}</div>', unsafe_allow_html=True)
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
                        animation: typing 1s steps(15, end) forwards;
                    }

                    .bot {
                        background-color: black;
                        overflow: hidden;
                        white-space: wrap;
                        width: 0;
                        animation: typing 1s steps(15, end) forwards;
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

            st.markdown('''
                <script>
                    setTimeout(function() {
                        document.getElementById('bot-message').innerHTML += ' {message}';
                    }, 2000);
                </script>
            ''', unsafe_allow_html=True)
            text_to_speech(output, st.session_state.question_number, selected_language)
    else:
        st.success(language_content[selected_language]['dialogue_completion'])

if __name__ == "__main__":
    home(selected_language)

# page_names_to_funcs = {
#     "Home": home,
# }



# selected_page = st.sidebar.selectbox("Select a page", page_names_to_funcs.keys())
# page_names_to_funcs[selected_page](selected_language)
