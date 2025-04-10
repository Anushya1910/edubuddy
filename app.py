import streamlit as st
import json
from gtts import gTTS
import os
import time
from fuzzywuzzy import process
from googletrans import Translator

# ========== Load data ==========
with open("resources.json", "r") as f:
    resources = json.load(f)

if not os.path.exists("history.json"):
    with open("history.json", "w") as f:
        json.dump([], f)

# ========== Streamlit Config ==========
st.set_page_config(page_title="EduBuddy", layout="centered")
st.title("📚 EduBuddy")
st.subheader("Voice-enabled regional learning assistant 🎙️🌐")

# ========== Voice Input ==========
use_voice = st.checkbox("🎙️ Use voice input (record your message)")
if use_voice:
    import speech_recognition as sr
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        st.info("🎧 Listening... Speak clearly.")
        try:
            audio = recognizer.listen(source, timeout=5)
            user_input = recognizer.recognize_google(audio)
            st.success(f"You said: {user_input}")
        except Exception as e:
            user_input = ""
            st.error("Sorry, I couldn't understand.")
else:
    user_input = st.text_input("📝 Type what you want to learn (e.g., 'math in tamil')")

# ========== Smart Detection ==========
def detect_subject_language(text):
    available_subjects = list(resources.keys())
    available_languages = ["tamil", "english"]
    
    subject = process.extractOne(text.lower(), available_subjects)[0]
    language = process.extractOne(text.lower(), available_languages)[0]
    
    return subject, language

# ========== Translate Text ==========
def translate_to_tamil(text):
    translator = Translator()
    result = translator.translate(text, dest="ta")
    return result.text

# ========== Show Resources ==========
def show_response(user_input):
    subject, language = detect_subject_language(user_input)

    st.markdown("🧑‍🎓 **You asked:** " + user_input)

    try:
        links = resources[subject][language]
        translated_heading = translate_to_tamil(f"EduBuddy suggests these {subject} resources in {language}:")

        st.markdown(f"🤖 **{translated_heading}**")
        for link in links:
            st.markdown(f"- [📎 {link}]({link})")

        # Save history
        with open("history.json", "r+") as f:
            history = json.load(f)
            history.append({"query": user_input, "subject": subject, "language": language})
            f.seek(0)
            json.dump(history, f, indent=4)
            f.truncate()

        # Optional: Text-to-Speech output in Tamil
        if language == "tamil":
            tts = gTTS(text=translated_heading, lang='ta')
            tts.save("speak.mp3")
            st.audio("speak.mp3", format="audio/mp3")

    except KeyError:
        st.warning("😢 Sorry, no matching resource found. Try a different subject or language.")

# ========== Run ==========
if user_input:
    show_response(user_input)

# ========== View History ==========
if st.checkbox("📖 Show my learning history"):
    with open("history.json", "r") as f:
        history = json.load(f)
        for item in reversed(history[-5:]):  # Show last 5
            st.markdown(f"- {item['query']} ➜ {item['subject'].capitalize()} in {item['language'].capitalize()}")
