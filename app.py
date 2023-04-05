import streamlit as st
from pytube import YouTube
from pathlib import Path
import shutil
import whisper
import os
import openai
from dotenv import load_dotenv

load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")

@st.cache_resource
def load_model():
    model = whisper.load_model("base")
    return model

def save_video(url, video_filename):
    youtubeObject = YouTube(url)
    youtubeObject = youtubeObject.streams.get_highest_resolution()
    try:
        youtubeObject.download()
    except:
        print("An error has occurred")
    print("Download is completed successfully")
    
    return video_filename

def save_audio(url):
    yt = YouTube(url)
    video = yt.streams.filter(only_audio=True).first()
    out_file = video.download()
    base, ext = os.path.splitext(out_file)
    file_name = base + '.mp3'
    try:
        os.rename(out_file, file_name)
    except WindowsError:
        os.remove(file_name)
        os.rename(out_file, file_name)
    audio_filename = Path(file_name).stem+'.mp3'
    video_filename = save_video(url, Path(file_name).stem+'.mp4')
    print(yt.title + " Has been successfully downloaded")
    return yt.title, audio_filename, video_filename

def audio_to_transcript(audio_file):
    model = load_model()
    result = model.transcribe(audio_file)
    transcript = result["text"]
    return transcript

def text_to_recipe(text):
    response = openai.Completion.create(
    model="text-davinci-003",
    prompt="Write the food recipe from the below text:\n"+text,
    temperature=0.7,
    max_tokens=600,
    top_p=1,
    frequency_penalty=0,
    presence_penalty=0
    )
    return response['choices'][0]['text']


st.set_page_config(layout="wide")

st.subheader("Food Recipe Generator App from Cooking Video")
url =  st.text_input('Enter URL of YouTube video:')

if url is not None:
    if st.button("Magic"):
        col1, col2, col3 = st.columns([1,1,1])
        with col1:
            st.info("Video uploaded successfully")
            video_title, audio_filename, video_filename = save_audio(url)
            st.video(video_filename)
        with col2:
            st.info("Transcript is below") 
            print(audio_filename)
            transcript_result = audio_to_transcript(audio_filename)
            st.success(transcript_result)
        with col3:
            st.info("Recipe is below") 
            recipe_result = text_to_recipe(transcript_result)
            st.success(recipe_result)