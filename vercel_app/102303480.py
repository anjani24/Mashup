import sys
import os
from yt_dlp import YoutubeDL
from moviepy.editor import AudioFileClip, concatenate_audioclips

DOWNLOAD_DIR = "downloads"
OUTPUT_DIR = "output"

def create_dirs():
    os.makedirs(DOWNLOAD_DIR, exist_ok=True)
    os.makedirs(OUTPUT_DIR, exist_ok=True)

# ------------------------------
# Download videos
# ------------------------------
def download_videos(singer, num_videos):
    print("Downloading videos...")

    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': f'{DOWNLOAD_DIR}/%(id)s.%(ext)s',
        'quiet': True,

        # More stable config
        'nocheckcertificate': True,
        'ignoreerrors': True,
        'geo_bypass': True,

        # Try cookies (optional)
        # 'cookiesfrombrowser': ('edge',),
    }

    search_query = f"ytsearch{num_videos}:{singer} songs"

    with YoutubeDL(ydl_opts) as ydl:
        ydl.download([search_query])

# ------------------------------
# Convert to mp3
# ------------------------------
def convert_to_audio():
    print("Converting to audio...")

    audio_files = []

    for file in os.listdir(DOWNLOAD_DIR):
        path = os.path.join(DOWNLOAD_DIR, file)

        if file.endswith((".webm", ".m4a", ".mp4")):
            output = os.path.join(DOWNLOAD_DIR, file.split('.')[0] + ".mp3")

            try:
                clip = AudioFileClip(path)
                clip.write_audiofile(output, verbose=False, logger=None)
                clip.close()

                audio_files.append(output)
            except Exception as e:
                print(f"Skipping {file}: {e}")

    if len(audio_files) == 0:
        raise Exception("No audio files found. Download failed.")

    return audio_files

# ------------------------------
# Trim audio
# ------------------------------
def trim_audio(files, duration):
    print("Trimming audio...")

    trimmed_clips = []

    for file in files:
        try:
            clip = AudioFileClip(file)
            trimmed = clip.subclip(0, duration)
            trimmed_clips.append(trimmed)
        except Exception as e:
            print(f"Error trimming {file}: {e}")

    if len(trimmed_clips) == 0:
        raise Exception("No valid audio clips after trimming.")

    return trimmed_clips

# ------------------------------
# Merge audio
# ------------------------------
def merge_audio(clips, output_file):
    print("Merging audio...")

    final_clip = concatenate_audioclips(clips)

    output_path = os.path.join(OUTPUT_DIR, output_file)
    final_clip.write_audiofile(output_path)

    # CLOSE ALL CLIPS (IMPORTANT)
    final_clip.close()
    for c in clips:
        c.close()

    print(f"Saved: {output_path}")

# ------------------------------
# Cleanup (optional)
# ------------------------------
def cleanup():
    for file in os.listdir(DOWNLOAD_DIR):
        os.remove(os.path.join(DOWNLOAD_DIR, file))

# ------------------------------
# Main
# ------------------------------
def main():
    if len(sys.argv) != 5:
        print("Usage: python program.py <SingerName> <NumberOfVideos> <AudioDuration> <OutputFileName>")
        sys.exit(1)

    singer = sys.argv[1]

    try:
        num_videos = int(sys.argv[2])
        duration = int(sys.argv[3])
    except ValueError:
        print("Error: NumberOfVideos and AudioDuration must be integers")
        sys.exit(1)

    output_file = sys.argv[4]

    # Validation
    if num_videos <= 10:
        print("Error: Number of videos must be > 10")
        sys.exit(1)

    if duration <= 20:
        print("Error: Duration must be > 20 seconds")
        sys.exit(1)

    try:
        create_dirs()

        download_videos(singer, num_videos)

        audio_files = convert_to_audio()

        trimmed_clips = trim_audio(audio_files, duration)

        merge_audio(trimmed_clips, output_file)

        cleanup()

        print("Mashup created successfully!")

    except Exception as e:
        print("Error:", str(e))

if __name__ == "__main__":
    main()
