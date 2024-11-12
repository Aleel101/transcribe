import streamlit as st
import os
import tempfile
import subprocess

# Get FFmpeg path from environment variable
FFMPEG_PATH = os.getenv("FFMPEG_PATH", "ffmpeg")  # Default to 'ffmpeg' if not set

def extract_audio(video_file, output_format, settings):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as temp_video:
        temp_video.write(video_file.read())
        temp_video_path = temp_video.name

    audio_file = temp_video_path.replace(".mp4", f".{output_format}")
    
    command = [FFMPEG_PATH, "-i", temp_video_path, "-vn"]
    
    if settings['hardware_accel'] != "None":
        if settings['hardware_accel'] == "NVIDIA NVENC":
            command.extend(["-c:a", "h264_nvenc"])
        elif settings['hardware_accel'] == "AMD AMF":
            command.extend(["-c:a", "h264_amf"])
        elif settings['hardware_accel'] == "Intel QSV":
            command.extend(["-c:a", "h264_qsv"])
    
    command.extend(["-threads", str(settings['thread_count'])])
    command.extend(["-preset", settings['encoding_preset']])
    
    if settings['audio_bitrate'] != "Default":
        command.extend(["-b:a", settings['audio_bitrate']])
    
    if settings['sample_rate'] != "Default":
        command.extend(["-ar", settings['sample_rate']])
    
    command.extend(["-acodec", output_format, audio_file])
    
    try:
        subprocess.run(command, check=True, capture_output=True, text=True)
        with open(audio_file, "rb") as f:
            audio_data = f.read()
        return audio_data
    except subprocess.CalledProcessError as e:
        st.error(f"Error during audio extraction: {e.stderr}")
        return None
    finally:
        os.unlink(temp_video_path)
        if os.path.exists(audio_file):
            os.unlink(audio_file)

st.set_page_config(page_title="Audio Extractor", layout="wide")

st.title("🎵 Audio Extractor")

# Custom CSS for improved appearance
st.markdown("""
<style>
    .stApp {
        max-width: 1200px;
        margin: 0 auto;
    }
    .uploadedFile {
        border: 2px dashed #1E90FF;
        border-radius: 10px;
        padding: 20px;
        text-align: center;
        background-color: #F0F8FF;
    }
    .uploadedFile:hover {
        background-color: #E6F3FF;
    }
    .stButton>button {
        width: 100%;
    }
</style>
""", unsafe_allow_html=True)

col1, col2 = st.columns([2, 1])

with col1:
    st.header("Upload and Extract")
    video_file = st.file_uploader("Drag and drop or click to upload a video file", type=["mp4", "avi", "mov", "mkv"], key="video_uploader")
    audio_format = st.selectbox("Select output audio format", ["mp3", "wav", "aac", "ogg"])

    if video_file is not None:
        st.markdown(f"<div class='uploadedFile'>File uploaded: {video_file.name}</div>", unsafe_allow_html=True)
        
        if st.button("Extract Audio"):
            with st.spinner("Extracting audio..."):
                audio_data = extract_audio(video_file, audio_format, st.session_state.settings)
            
            if audio_data:
                st.success("Audio extracted successfully!")
                
                st.download_button(
                    label="Download Extracted Audio",
                    data=audio_data,
                    file_name=video_file.name.replace(os.path.splitext(video_file.name)[1], f".{audio_format}"),
                    mime=f"audio/{audio_format}"
                )
            else:
                st.error("Failed to extract audio. Please check if FFmpeg is installed and the FFMPEG_PATH is set correctly.")

with col2:
    st.header("Settings")
    
    with st.expander("Advanced Settings", expanded=True):
        if 'settings' not in st.session_state:
            st.session_state.settings = {
                'hardware_accel': "None",
                'thread_count': 0,
                'encoding_preset': "medium",
                'audio_bitrate': "Default",
                'sample_rate': "Default"
            }
        
        st.session_state.settings['hardware_accel'] = st.selectbox(
            "Hardware Acceleration",
            ["None", "NVIDIA NVENC", "AMD AMF", "Intel QSV"],
            index=["None", "NVIDIA NVENC", "AMD AMF", "Intel QSV"].index(st.session_state.settings['hardware_accel'])
        )
        
        st.session_state.settings['thread_count'] = st.slider("Thread Count", 0, 64, st.session_state.settings['thread_count'])
        
        st.session_state.settings['encoding_preset'] = st.select_slider(
            "Encoding Preset",
            options=["ultrafast", "superfast", "veryfast", "faster", "fast", "medium", "slow", "slower", "veryslow"],
            value=st.session_state.settings['encoding_preset']
        )
        
        st.session_state.settings['audio_bitrate'] = st.selectbox(
            "Audio Bitrate",
            ["Default", "64k", "128k", "192k", "256k", "320k"],
            index=["Default", "64k", "128k", "192k", "256k", "320k"].index(st.session_state.settings['audio_bitrate'])
        )
        
        st.session_state.settings['sample_rate'] = st.selectbox(
            "Sample Rate",
            ["Default", "44100", "48000", "96000"],
            index=["Default", "44100", "48000", "96000"].index(st.session_state.settings['sample_rate'])
        )

st.markdown("---")

# Instructions
st.header("📘 Instructions")
st.markdown("""
1. Drag and drop a video file or click to upload.
2. Select the desired output audio format.
3. Adjust advanced settings if needed.
4. Click the 'Extract Audio' button to process the video.
5. Download the extracted audio file.
""")

# Note about file size limit
st.info("Note: The default file size limit is 20GB. To increase this limit, you need to configure the `server.maxUploadSize` option in your Streamlit configuration.")

