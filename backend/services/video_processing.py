# Functions for video processing, e.g., frame extraction, audio transcription

import cv2
from moviepy.editor import VideoFileClip
# from pydub import AudioSegment # For audio manipulation if needed
# import speech_recognition as sr # For STT

def extract_frames(video_path: str, output_folder: str, frame_interval: int = 1):
    """
    Extracts frames from a video file at a given interval (in seconds).
    Saves frames as images in the output_folder.
    Returns a list of paths to the extracted frames.
    """
    import os
    os.makedirs(output_folder, exist_ok=True)

    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise ValueError(f"Could not open video file: {video_path}")

    fps = cap.get(cv2.CAP_PROP_FPS)
    frame_count = 0
    saved_frame_count = 0
    frame_paths = []

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        current_time_sec = frame_count / fps
        if current_time_sec >= saved_frame_count * frame_interval:
            frame_filename = os.path.join(output_folder, f"frame_{saved_frame_count}.jpg")
            cv2.imwrite(frame_filename, frame)
            frame_paths.append(frame_filename)
            saved_frame_count += 1

        frame_count += 1

    cap.release()
    return frame_paths

def extract_audio(video_path: str, audio_output_path: str):
    """
    Extracts audio from a video file and saves it.
    Returns the path to the extracted audio file.
    """
    try:
        video_clip = VideoFileClip(video_path)
        audio_clip = video_clip.audio
        if audio_clip:
            audio_clip.write_audiofile(audio_output_path, codec='pcm_s16le') # WAV for easier processing by STT
            audio_clip.close()
            video_clip.close()
            return audio_output_path
        else:
            video_clip.close()
            return None
    except Exception as e:
        print(f"Error extracting audio from {video_path}: {e}")
        return None

# def transcribe_audio(audio_path: str):
#     """
#     Transcribes audio file to text using SpeechRecognition.
#     This is a basic implementation and might need a more robust STT service for production.
#     """
#     if not audio_path:
#         return ""

#     r = sr.Recognizer()
#     try:
#         with sr.AudioFile(audio_path) as source:
#             audio_data = r.record(source)
#         text = r.recognize_google(audio_data) # Uses Google Web Speech API
#         return text
#     except sr.UnknownValueError:
#         print("Google Speech Recognition could not understand audio")
#         return ""
#     except sr.RequestError as e:
#         print(f"Could not request results from Google Speech Recognition service; {e}")
#         return ""
#     except Exception as e:
#         print(f"Error during audio transcription: {e}")
#         return ""

# Placeholder for a more robust STT solution, Whisper integration will happen later.
def transcribe_audio_placeholder(audio_path: str):
    if audio_path:
        print(f"Placeholder: Would transcribe audio from {audio_path}")
        return "This is a placeholder for transcribed audio from the video."
    return ""
