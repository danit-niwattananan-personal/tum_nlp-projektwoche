import os
from moviepy.video.io.VideoFileClip import VideoFileClip 

def extract_audio_from_video(video_path, output_dir, overwrite=False):
    os.makedirs(output_dir, exist_ok=True)
    base = os.path.basename(video_path)
    name, _ = os.path.splitext(base)
    audio_path = os.path.join(output_dir, f"{name}.wav")

    if os.path.exists(audio_path) and not overwrite:
        print(f"Audio already exists: {audio_path}")
        return audio_path

    print(f"Extracting audio from {video_path}...")
    video = VideoFileClip(video_path)
    video.audio.write_audiofile(audio_path, codec='pcm_s16le')
    return audio_path

def batch_extract(trailer_dir, output_dir):
    for filename in os.listdir(trailer_dir):
        if filename.endswith(".mp4"):
            video_path = os.path.join(trailer_dir, filename)
            extract_audio_from_video(video_path, output_dir)

if __name__ == "__main__":
    trailer_dir = "data/trailers"
    output_dir = "data/audio"
    batch_extract(trailer_dir, output_dir)
