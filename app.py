from pytube import YouTube
import streamlit as st
import os
from pathlib import Path
import logging
from pytube.innertube import InnerTube
import yt_dlp
import tempfile

def normalize_url(url):
    if 'youtu.be' in url:
        video_id = url.split('/')[-1]
        return f'https://youtube.com/watch?v={video_id}'
    return url

def get_youtube_object(url):
    return YouTube(url)

def get_ffmpeg_path():
    """Get ffmpeg path based on platform"""
    import shutil
    ffmpeg_path = shutil.which('ffmpeg')
    if ffmpeg_path:
        return ffmpeg_path
    
    # Check common locations
    common_locations = [
        '/usr/bin/ffmpeg',
        '/usr/local/bin/ffmpeg',
        'C:\\ffmpeg\\bin\\ffmpeg.exe'
    ]
    
    for location in common_locations:
        if os.path.exists(location):
            return location
            
    return None

def download_video(url, format_type):
    try:
        # Create a temporary directory for downloads
        with tempfile.TemporaryDirectory() as temp_dir:
            # Base options for both formats
            base_opts = {
                'quiet': True,
                'no_warnings': True,
                'outtmpl': os.path.join(temp_dir, '%(title)s.%(ext)s'),
            }
            
            # Add ffmpeg location if found
            ffmpeg_path = get_ffmpeg_path()
            if ffmpeg_path:
                base_opts['ffmpeg_location'] = ffmpeg_path

            # Configure yt-dlp options based on format
            if format_type == "MP3":
                ydl_opts = {
                    **base_opts,
                    'format': 'bestaudio/best',
                    'postprocessors': [{
                        'key': 'FFmpegExtractAudio',
                        'preferredcodec': 'mp3',
                        'preferredquality': '192',
                    }],
                }
            else:  # MP4
                ydl_opts = {
                    **base_opts,
                    'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
                }
            
            # First get video info
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                
                if info:
                    # Display video details
                    st.write(f"Title: {info['title']}")
                    st.write(f"Duration: {int(info['duration'])} seconds")
                    
                    # Add download button
                    if st.button("Download"):
                        with st.spinner("Downloading..."):
                            # Download the video
                            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                                ydl.download([url])
                                
                            # Find the downloaded file
                            downloaded_files = os.listdir(temp_dir)
                            if downloaded_files:
                                file_path = os.path.join(temp_dir, downloaded_files[0])
                                
                                # Read the file and create a download button
                                with open(file_path, 'rb') as f:
                                    file_data = f.read()
                                    file_ext = '.mp3' if format_type == "MP3" else '.mp4'
                                    file_name = f"{info['title']}{file_ext}"
                                    st.download_button(
                                        label="Click to save file",
                                        data=file_data,
                                        file_name=file_name,
                                        mime=f"{'audio/mp3' if format_type == 'MP3' else 'video/mp4'}"
                                    )
                else:
                    st.error("Could not fetch video information")
                    
    except Exception as e:
        st.error(f"Error: {str(e)}")

def main():
    st.title("YouTube Video Downloader")
    
    # Get video URL from user
    video_url = st.text_input("Enter YouTube Video URL:")
    
    # Format selection
    format_type = st.radio(
        "Select Format",
        ["MP4", "MP3"],
        horizontal=True
    )
    
    if video_url:
        download_video(video_url, format_type)

def progress_callback(stream, chunk, bytes_remaining):
    total_size = stream.filesize
    bytes_downloaded = total_size - bytes_remaining
    percentage = (bytes_downloaded / total_size) * 100
    st.progress(int(percentage))

def complete_callback(stream, file_path):
    st.write("Download Complete!")

if __name__ == "__main__":
    main()
