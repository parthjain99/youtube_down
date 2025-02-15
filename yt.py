import yt_dlp

def download_video(url, output_path=None):
    ydl_opts = {
        'format': 'best',  # Download best quality
        'outtmpl': '%(title)s.%(ext)s' if not output_path else output_path,
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # Get video info
            info = ydl.extract_info(url, download=False)
            print(f"Title: {info.get('title')}")
            print(f"Duration: {info.get('duration')} seconds")
            
            # Download the video
            ydl.download([url])
            return True
    except Exception as e:
        print(f"Error: {str(e)}")
        return False

# Example usage
url = 'https://www.youtube.com/watch?v=2lAe1cqCOXo'
download_video(url)