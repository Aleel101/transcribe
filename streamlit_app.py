import streamlit as st

st.title("Guide for Setting Up FFmpeg")

st.write("This guide will help you set up FFmpeg on your system so that you can use it to process video and audio files.")

st.header("Step 1: Download FFmpeg")

st.markdown("""
1. Visit the official FFmpeg download page: https://ffmpeg.org/download.html
2. Scroll down to the 'Get packages & executable files' section.
3. Choose your operating system:
   - For Windows: Click on 'Windows builds from gyan.dev'
   - For macOS: Click on 'Static builds for macOS 64-bit'
   - For Linux: Use your distribution's package manager (see Step 2)
4. Download the appropriate version for your system.
""")

st.header("Step 2: Install FFmpeg")

os_option = st.selectbox("Select your operating system:", ["Windows", "macOS", "Linux"])

if os_option == "Windows":
    st.markdown("""
    1. Extract the downloaded zip file to a folder of your choice (e.g., C:\\ffmpeg).
    2. Add FFmpeg to your system PATH:
       - Go to the Searchbar and type 'Environment Variables'
       - Click on 'Edit the system environment variables'
       - Click on 'Environment Variables'
       - Under 'System variables', find and select the 'Path' variable, then click 'Edit'
       - Click 'New' and add the path to the FFmpeg 'bin' folder (e.g., C:\\ffmpeg\\bin)
       - Click 'OK' to close all windows
    3. Restart your computer to apply the changes
    """)
elif os_option == "macOS":
    st.markdown("""
    1. Install Homebrew if you haven't already:
       ```
       /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
       ```
    2. Install FFmpeg using Homebrew:
       ```
       brew install ffmpeg
       ```
    """)
elif os_option == "Linux":
    st.markdown("""
    Use your distribution's package manager to install FFmpeg:
    
    - Ubuntu or Debian:
      ```
      sudo apt update
      sudo apt install ffmpeg
      ```
    
    - Fedora:
      ```
      sudo dnf install ffmpeg
      ```
    
    - Arch Linux:
      ```
      sudo pacman -S ffmpeg
      ```
    """)

st.header("Step 3: Verify the Installation")

st.markdown("""
1. Click the button below to check if FFmpeg is installed and accessible from your system path.
""")

if st.button("Verify FFmpeg Installation"):
    import subprocess

    try:
        result = subprocess.run(["ffmpeg", "-version"], capture_output=True, text=True, check=True)
        st.success(f"FFmpeg is installed! Version: {result.stdout.splitlines()[0]}")
    except FileNotFoundError as e:
        st.error(f"FFmpeg not found. Please make sure it's installed and added to your system PATH.")
