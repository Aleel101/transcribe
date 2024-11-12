import streamlit as st
import whisper
import tempfile
import os
import time
import json
from datetime import datetime
import csv
from io import StringIO

def format_time(seconds):
    """Convert seconds to HH:MM:SS format"""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    seconds = int(seconds % 60)
    milliseconds = int((seconds % 1) * 1000)
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}"

def create_srt_content(segments):
    """Create SRT format content from segments"""
    srt_content = ""
    for i, segment in enumerate(segments, 1):
        start = format_time(segment['start']) + ",000"
        end = format_time(segment['end']) + ",000"
        srt_content += f"{i}\n{start} --> {end}\n{segment['text']}\n\n"
    return srt_content

def create_vtt_content(segments):
    """Create VTT format content from segments"""
    vtt_content = "WEBVTT\n\n"
    for i, segment in enumerate(segments, 1):
        start = format_time(segment['start'])
        end = format_time(segment['end'])
        vtt_content += f"{start}.000 --> {end}.000\n{segment['text']}\n\n"
    return vtt_content

def create_tsv_content(segments):
    """Create TSV format content from segments"""
    output = StringIO()
    writer = csv.writer(output, delimiter='\t')
    writer.writerow(['Start', 'End', 'Text'])
    for segment in segments:
        writer.writerow([format_time(segment['start']), 
                        format_time(segment['end']), 
                        segment['text']])
    return output.getvalue()

def transcribe_audio(audio_file, model_name, language, task, progress_bar):
    # Load the Whisper model
    model = whisper.load_model(model_name)
    
    # Save the uploaded file temporarily
    with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(audio_file.name)[1]) as tmp_file:
        tmp_file.write(audio_file.getvalue())
        tmp_file_path = tmp_file.name

    try:
        # Start transcription
        start_time = time.time()
        
        # Use a simple progress simulation
        for i in range(100):
            time.sleep(0.1)  # Simulate progress
            progress_bar.progress(i/100)
            
        # Transcribe the audio
        if task == "transcribe":
            result = model.transcribe(tmp_file_path, language=language if language else None)
        else:  # translate
            result = model.transcribe(tmp_file_path, task="translate", language=language if language else None)
        
        progress_bar.progress(1.0)
        
        return result
    
    finally:
        # Clean up the temporary file
        os.unlink(tmp_file_path)

def transcribe_page():
    st.set_page_config(page_title="Audio Transcription Tool", layout="wide")
    
    # Custom CSS
    st.markdown("""
        <style>
        .main {
            padding: 2rem;
        }
        .stButton>button {
            width: 100%;
        }
        .output-section {
            margin-top: 2rem;
            padding: 1rem;
            border-radius: 0.5rem;
            background-color: #f0f2f6;
        }
        </style>
    """, unsafe_allow_html=True)

    # Title with icon
    st.title("🎙️ Audio Transcription Tool")

    # Create two columns for layout
    col1, col2 = st.columns([2, 1])

    with col1:
        # File upload with drag and drop
        audio_file = st.file_uploader("Drop your audio file here or click to upload", 
                                    type=["wav", "mp3", "m4a"],
                                    help="Supported formats: WAV, MP3, M4A")

    with col2:
        # Settings in a card
        with st.expander("⚙️ Transcription Settings", expanded=True):
            selected_model = st.selectbox("Model Size", 
                                        ["tiny", "base", "small", "medium", "large"],
                                        index=1,
                                        help="Larger models are more accurate but slower")
            
            language = st.text_input("Language Code (optional)", 
                                   help="e.g., 'en' for English, leave empty for auto-detection")
            
            task = st.selectbox("Task Type",
                              ["transcribe", "translate"],
                              help="'translate' will translate to English")
            
            output_format = st.multiselect("Output Formats",
                                         ["txt", "vtt", "srt", "tsv", "json"],
                                         default=["txt"],
                                         help="Select one or more output formats")

    # Transcribe button
    if audio_file is not None:
        if st.button("🎯 Start Transcription"):
            try:
                # Progress bar
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                # Transcribe
                status_text.text("Transcribing... Please wait")
                result = transcribe_audio(audio_file, selected_model, language, task, progress_bar)
                
                # Success message
                st.success("✨ Transcription completed successfully!")
                
                # Display results in tabs
                tabs = st.tabs(["Preview"] + output_format)
                
                # Preview tab
                with tabs[0]:
                    st.text_area("Transcription Result", result["text"], height=300)
                
                # Generate different formats
                for i, format_type in enumerate(output_format, 1):
                    with tabs[i]:
                        if format_type == "txt":
                            content = result["text"]
                            mime_type = "text/plain"
                        elif format_type == "json":
                            content = json.dumps(result, indent=2)
                            mime_type = "application/json"
                        elif format_type == "srt":
                            content = create_srt_content(result["segments"])
                            mime_type = "text/srt"
                        elif format_type == "vtt":
                            content = create_vtt_content(result["segments"])
                            mime_type = "text/vtt"
                        elif format_type == "tsv":
                            content = create_tsv_content(result["segments"])
                            mime_type = "text/tab-separated-values"
                        
                        st.text_area(f"{format_type.upper()} Output", content, height=300)
                        
                        # Download button
                        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                        filename = f"transcription_{timestamp}.{format_type}"
                        st.download_button(
                            label=f"Download {format_type.upper()} File",
                            data=content,
                            file_name=filename,
                            mime=mime_type
                        )
                
            except Exception as e:
                st.error(f"❌ Error during transcription: {str(e)}")
                
        else:
            st.info("👆 Click the button above to start transcription")
    else:
        st.info("Please upload an audio file to begin")

if __name__ == "__main__":
    transcribe_page()