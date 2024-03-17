import streamlit as st
from pathlib import Path
import base64

st.title("Streamlit Image Button Example")
st.write("Hassan Mustafa")
st.write("This is a Streamlit app with five clickable image buttons.")

def img_to_bytes(img_path):
    img_bytes = Path(img_path).read_bytes()
    encoded_img = base64.b64encode(img_bytes).decode()
    return encoded_img

# Replace 'path_to_your_image.png' with the actual path to your image file
# image_paths = ['english_text.png', 'urdu_text.png', 'spanish_text.png', 'bangla_text.png', 'arabic_text.png']
image_paths = ['images/english.png', 'images/urdu.png', 'images/spanish.png', 'images/bangla.png', 'images/arabic.png']


for image_path in image_paths:
    image_base64 = img_to_bytes(image_path)
    html = f"<img src='data:image/png;base64,{image_base64}'>"
    st.markdown(html, unsafe_allow_html=True)
    if st.button(f"Button for {image_path}"):
        st.success(f"Button is clicked!")


# ------------------------------------------------------------
st.divider()
st.markdown(
            "###### [![this is an image link](https://i.imgur.com/mQAQwvt.png)](https://accounts.google.com/o/oauth2/auth?response_type=code&client_id=686079794781-0bt8ot3ie81iii7i17far5vj4s0p20t7.apps.googleusercontent.com&redirect_uri=urn%3Aietf%3Awg%3Aoauth%3A2.0%3Aoob&scope=https%3A%2F%2Fwww.googleapis.com%2Fauth%2Fwebmasters.readonly&state=vryYlMrqKikWGlFVwqhnMpfqr1HMiq&prompt=consent&access_type=offline)"
        )
# -------------------------------------------------------------

st.divider()


import base64
import streamlit as st
from st_clickable_images import clickable_images

def pass_value(image_index):
    values = ["English", "Urdu", "Spanish", "Bangla", "Arabic"]
    selected_value = values[image_index]
    st.success(f'The selected language is: {selected_value}')
    # You can perform other actions with the selected value here

images = []
for file in ["images/english.png", 
             "images/urdu.png",
             "images/spanish.png",
             "images/bangla.png",
             "images/arabic.png",]:
    with open(file, "rb") as image:
        encoded = base64.b64encode(image.read()).decode()
        images.append(f"data:image/jpeg;base64,{encoded}")

clicked = clickable_images(
    images,
    titles=[f"Image #{str(i)}" for i in range(2)],
    div_style={"display": "flex", "justify-content": "center", "flex-wrap": "wrap"},
    img_style={"margin": "5px", "height": "50px"},
)

st.markdown(f"Image #{clicked} clicked" if clicked > -1 else "No image clicked")

# Check if an image was clicked
if clicked > -1:
    pass_value(clicked)
else:
    st.warning("Choose the language first.")

# ------------------------------------------------------------------

st.divider()

