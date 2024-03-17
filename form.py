import streamlit as st
import base64
from st_clickable_images import clickable_images
from fpdf import FPDF


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
    }
}

questions = [
        # Dialogue 1
        ("What is your name?", "1", "آپ کا نام کيا ہے?", "¿Cómo te llamas?", "আপনার নাম কি?", "ما اسمك؟"),
        ("What is your age?", "2", "آپ کی عمر کیا ہے؟", "¿Cuántos años tienes?", "আপনার বয়স কত?", "ما هو عمرك؟"),
        # Dialogue 2
        ("Are you taking any Medications? If yes, then please tell the name of the medicines.", "3", "کیا آپ کوئی دوا لے رہے ہیں؟اگر ہاں. پھر دوا کا نام بتائیں ", "¿Está tomando algún medicamento? En caso afirmativo, indique el nombre del medicamento.", "আপনি কি কোনো ওষুধ খাচ্ছেন? যদি হ্যাঁ, তাহলে ওষুধের নাম বলুন।", "هل أنت مع أي أدوية؟ إذا كانت الإجابة بنعم، يرجى ذكر اسم الدواء."),
        # Dialogue 3
        ("What is your major complaint?", "4", "آپ کی سب سے بڑی شکایت کیا ہے؟ ", "¿Cuál es su principal queja?", "আপনার প্রধান অভিযোগ কি?", "ما هي شكواك الرئيسية؟"),
        # Dialogue 4 (Relationships)
        ("Are you adopted? If yes, at what age were you adopted?", "5", "کیا آپ کو گود لیا گیا ہے؟ اگر ہاں، تو آپ کو کس عمر میں گود لیا گیا تھا؟", "¿Eres adoptado? En caso afirmativo, ¿a qué edad fue adoptado?", "আপনি কি দত্তক নিয়েছেন? যদি হ্যাঁ, কোন বয়সে আপনাকে দত্তক নেওয়া হয়েছিল?", "هل تم تبنيك؟ إذا كانت الإجابة بنعم ، في أي عمر تم تبنيك؟"),
        ("How is your relationship with your parents?", "6", "والدین کے ساتھ آپ کے تعلقات کیسے ہیں؟", "¿Cómo es tu relación con tus padres?", "বাবা-মায়ের সঙ্গে আপনার সম্পর্ক কেমন?", "كيف هي علاقتك مع والديك؟"),
        ("Are your parents married?", "7", "کیا آپ کے والدین شادی شدہ ہیں؟", "¿Tus padres están casados?", "তোমার বাবা-মা কি বিবাহিত?", "هل والداك متزوجان؟"),
    ]
language_mapping = {
        'English': 'en',
        'Urdu': 'ur',
        'Spanish': 'es',
        'Bangla': 'bn',
        'Arabic': 'ar'
    }

def create_download_link(val, filename):
    b64 = base64.b64encode(val)  # val looks like b'...'
    return f'<a href="data:application/octet-stream;base64,{b64.decode()}" download="{filename}.pdf">Download file</a>'

def main(selected_value):
    mapped_language = language_mapping.get(selected_value, 'en')
    st.header(language_content[mapped_language]['header'], divider='orange')

    user_responses = {}

    for i, (English, key, Urdu, Spanish, Bangla, Arabic) in enumerate(questions):
        # Choose the appropriate language based on the selected_value
        if selected_value == "English":
            question_text = English
        elif selected_value == "Urdu":
            question_text = Urdu
        elif selected_value == "Spanish":
            question_text = Spanish
        elif selected_value == "Bangla":
            question_text = Bangla
        elif selected_value == "Arabic":
            question_text = Arabic
        else:
            # Default to English if the selected_value is not recognized
            question_text = English

        # Display the input field with the translated question
        if key == "1" or key == "2":
            response = st.text_input(question_text, key=key)
        elif key == "3":
            response = st.text_area(question_text, key=key)
        elif key == "4":
            response = st.text_input(question_text, key=key)
        elif key == "5":
            response = st.text_input(question_text, key=key)
        elif key == "6":
            response = st.text_input(question_text, key=key)
        elif key == "7":
            response = st.text_input(question_text, key=key)

        user_responses[key] = {"Q-": question_text, "A-": response}

    st.write("User Responses:", user_responses)
    
    export_as_pdf = st.button("Export Report")
    if export_as_pdf:
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font('Arial', '', 10)
        pdf.cell(40, 20, f"{language_content[mapped_language]['header']}", ln=True)
        for key, response_dict in user_responses.items():
            pdf.cell(0, 10, f"Q: {response_dict['Q-']}", ln=True)
            pdf.cell(0, 10, f"A: {response_dict['A-']}", ln=True)
            pdf.cell(0, 10, "------------------------------------------------------------------------------------------------------------------------------------------------------------", ln=True)

        html = create_download_link(pdf.output(dest="S").encode("latin-1"), "test")
        st.markdown(html, unsafe_allow_html=True)

def pass_value(image_index):
    values = ["English", "Urdu", "Spanish", "Bangla", "Arabic"]
    selected_value = values[image_index]
    st.success(f'The selected language is: {selected_value}')
    return selected_value

images = []
for file in ["images/english.png", 
             "images/urdu.png",
             "images/spanish.png",
             "images/bangla.png",
             "images/arabic.png",]:
    with open(file, "rb") as image:
        encoded = base64.b64encode(image.read()).decode()
        images.append(f"data:image/jpeg;base64,{encoded}")

with st.sidebar:
    clicked = clickable_images(
        images,
        titles=[f"Click on image to select the language." for i in range(2)],
        div_style={"display": "flex", "justify-content": "center", "flex-wrap": "wrap"},
        img_style={"margin": "5px", "height": "50px"},
    )
    # Check if an image was clicked
    if clicked > -1:
        selected_value = pass_value(clicked)
    else:
        selected_value = 'English'

if __name__ == "__main__":
    main(selected_value)