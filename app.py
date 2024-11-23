import streamlit as st
from yt_dlp import YoutubeDL
import os
import subprocess

# Streamlit UI
st.title("YouTube Audio Pitch Shifter")
st.write("YouTube 링크를 입력한 뒤 조옮김 합니다. (ex. 1은 반키 up, -1은 반키 down)")

# Session state for managing process
if "processed" not in st.session_state:
    st.session_state["processed"] = False

# Input form
youtube_link = st.text_input("YouTube Link:")
key_change = st.slider("Pitch Shift (Semitones)", min_value=-12, max_value=12, value=0)

if st.button("Process"):
    if youtube_link:
        if not st.session_state["processed"]:  # Avoid repeated processing
            try:
                # Step 1: Download audio using yt-dlp
                st.write("Downloading audio...")
                ydl_opts = {
                    'format': 'bestaudio/best',
                    'outtmpl': 'input_audio.%(ext)s',
                }
                with YoutubeDL(ydl_opts) as ydl:
                    ydl.download([youtube_link])
                input_audio = "input_audio.webm"  # Default format
                st.write("Audio downloaded successfully.")

                # Step 2: Convert to WAV
                st.write("Converting to WAV format...")
                wav_file = "audio.wav"
                subprocess.run(["ffmpeg", "-i", input_audio, wav_file, "-y"], check=True)

                # Step 3: Change key using Rubber Band Library
                st.write("Changing audio key...")
                shifted_wav_file = "shifted_audio.wav"
                subprocess.run([
                    "rubberband", 
                    f"-p {key_change}",  # Pitch shift
                    wav_file, 
                    shifted_wav_file
                ], check=True)
                st.write("Key change applied successfully.")

                # Step 4: Convert shifted WAV to MP3
                shifted_mp3_file = "shifted_audio.mp3"
                subprocess.run(["ffmpeg", "-i", shifted_wav_file, shifted_mp3_file, "-y"], check=True)
                st.write("Converted to MP3 successfully.")

                # Step 5: Audio preview in Streamlit
                st.audio(shifted_mp3_file, format="audio/mp3")

                # Step 6: Allow user to download MP3 file
                with open(shifted_mp3_file, "rb") as file:
                    st.download_button(
                        label="Download Processed MP3",
                        data=file,
                        file_name="processed_audio.mp3",
                        mime="audio/mp3"
                    )

                # Mark as processed
                st.session_state["processed"] = True

                # Cleanup
                os.remove(input_audio)
                os.remove(wav_file)
                os.remove(shifted_wav_file)
                os.remove(shifted_mp3_file)
            except Exception as e:
                st.error(f"An error occurred: {e}")
        else:
            st.warning("Audio already processed. Reload the page to start a new process.")
    else:
        st.warning("Please provide a valid YouTube link.")
