from pydub import AudioSegment
from moviepy.editor import VideoFileClip, AudioFileClip
import os

from audio_redactor import redact_words
from video_redactor import redact_video

def redact_audio(video_path, audio_output):
    video_clip = VideoFileClip(video_path)
    
    # Extract the original audio from the video
    original_audio = video_clip.audio
    temp_original_audio_path = "temp_original_audio.wav"
    original_audio.write_audiofile(temp_original_audio_path)

    redact_words(temp_original_audio_path, audio_output)

    os.remove(temp_original_audio_path)

def combine_channels(output, video, audio):
    new_video = VideoFileClip(video)
    new_audio = AudioFileClip(audio)
    new_video = new_video.set_audio(new_audio)
    new_video.write_videofile(output, codec='libx264', audio_codec='aac')

if __name__ == "__main__":
    video_path = "example.mp4"
    redacted_audio_path = "temp_audio.wav"
    redacted_video_path = "temp_video.mp4"

    redact_audio(video_path, redacted_audio_path)
    redact_video(video_path, redacted_video_path)

    combine_channels(output="output.mp4", video=redacted_video_path, audio=redacted_audio_path)
    os.remove(redacted_audio_path)
    os.remove(redacted_video_path)