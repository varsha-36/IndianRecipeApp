import streamlit as st
import json
import os
from datetime import datetime
from gtts import gTTS
import tempfile

# ------------------------------
# File paths
# ------------------------------
DATA_FILE = "recipes.json"
VIDEO_FOLDER = "videos"
os.makedirs(VIDEO_FOLDER, exist_ok=True)

# ------------------------------
# Load and Save Recipes
# ------------------------------
def load_recipes():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def save_recipes(recipes):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(recipes, f, indent=4, ensure_ascii=False)

def add_recipe(name, ingredients, steps, video_file):
    recipes = load_recipes()
    recipe = {
        "name": name,
        "ingredients": ingredients,
        "steps": steps,
        "video": video_file if video_file else None,
        "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    recipes.append(recipe)
    save_recipes(recipes)

# ------------------------------
# AI Translation
# ------------------------------
@st.cache_resource
def get_translation_pipeline(src_lang="en", tgt_lang="hi"):
    model_name = f"Helsinki-NLP/opus-mt-{src_lang}-{tgt_lang}"
    return pipeline("translation", model=model_name)

def translate_text(text, src="en", tgt="hi"):
    try:
        translator = get_translation_pipeline(src, tgt)
        translated = translator(text, max_length=512)
        return translated[0]['translation_text']
    except Exception as e:
        return f"Translation error: {e}"

# ------------------------------
# Text-to-Speech (TTS)
# ------------------------------
def read_text_aloud(text, lang="en"):
    try:
        tts = gTTS(text=text, lang=lang)
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as temp_audio_file:
            tts.save(temp_audio_file.name)
            st.audio(temp_audio_file.name, format="audio/mp3")
    except Exception as e:
        st.error(f"Error in TTS: {e}")

# ------------------------------
# Streamlit UI
# ------------------------------
st.set_page_config(page_title="Indian Recipe Exchange", layout="wide")
st.title("🍛 Indian Recipe Exchange")
st.write("Share your favorite recipes in **text or video** form, and explore recipes from others!")

# Sidebar - Language Selection
st.sidebar.subheader("🌐 Language Options")
language_map = {"English": "en", "Hindi": "hi", "Telugu": "te"}
selected_language = st.sidebar.selectbox("Select Language", list(language_map.keys()))
selected_lang_code = language_map[selected_language]

menu = st.sidebar.radio("Menu", ["Add Recipe", "Browse Recipes"], index=0)

# ------------------------------
# Add Recipe
# ------------------------------
if menu == "Add Recipe":
    st.subheader("Add a New Recipe")
    name = st.text_input("Recipe Name")
    ingredients = st.text_area("Ingredients (one per line)")
    steps = st.text_area("Preparation Steps")
    video = st.file_uploader("Upload a video (optional)", type=["mp4", "mov", "avi"])

    if st.button("Submit"):
        video_path = None
        if video:
            video_path = os.path.join(VIDEO_FOLDER, video.name)
            with open(video_path, "wb") as f:
                f.write(video.read())
        add_recipe(name, ingredients, steps, video_path)
        st.success("✅ Recipe added successfully!")

# ------------------------------
# Browse Recipes
# ------------------------------
elif menu == "Browse Recipes":
    st.subheader("Browse Recipes")
    recipes = load_recipes()

    if not recipes:
        st.info("No recipes added yet.")
    else:
        for idx, recipe in enumerate(recipes):
            st.write(f"### {recipe['name']}")
            st.write("**Ingredients:**")
            st.write(recipe["ingredients"])
            st.write("**Steps:**")
            st.write(recipe["steps"])

            # TTS Button
            if st.button(f"🔊 Listen to Recipe {idx+1} in {selected_language}"):
                text_to_read = f"Recipe Name: {recipe['name']}. Ingredients: {recipe['ingredients']}. Steps: {recipe['steps']}."
                read_text_aloud(text_to_read, lang=selected_lang_code)

            # Translation Feature
            if st.button(f"Translate Recipe {idx+1} to {selected_language}"):
                translated_name = translate_text(recipe['name'], src="en", tgt=selected_lang_code)
                translated_ingredients = translate_text(recipe['ingredients'], src="en", tgt=selected_lang_code)
                translated_steps = translate_text(recipe['steps'], src="en", tgt=selected_lang_code)
                st.write(f"**Recipe Name ({selected_language}):** {translated_name}")
                st.write(f"**Ingredients ({selected_language}):** {translated_ingredients}")
                st.write(f"**Steps ({selected_language}):** {translated_steps}")

            # Display video if available
            if recipe["video"]:
                st.video(recipe["video"])
            st.write("---")
