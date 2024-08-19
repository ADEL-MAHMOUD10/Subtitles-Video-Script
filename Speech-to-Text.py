# Install all library by pip install library in terminal 
import requests # pip install requests
import time # pip install time
from tkinter import filedialog # pip install tk
import moviepy.editor # pip install moviepy

def video_to_audio():
    print("_"*23+"CONVERT"+"_"*23)
    print("Select Video to convert it to Audio file for best translate")
    video_name = filedialog.askopenfilename(title="Select Video", filetypes=[("Video Files", "*.mp4;*.wmv;*.mov;*.mkv;*.H.264")])
    if not video_name:
        print("No file selected.")
        return None

    with open(video_name, "rb") as file:
        video_size = len(file.read())
        print(f"File size: {(video_size) * 0.000001:.2f}MB")

    video = moviepy.editor.VideoFileClip(video_name)
    print("Video uploaded...")
    audio_file_name = "audio.mp3"
    audio = video.audio
    audio.write_audiofile(audio_file_name)

    with open(audio_file_name, "rb") as f:
        audio_size = len(f.read())
        print(f"File size: {(audio_size) * 0.000001:.2f}MB")
    print(f"File name: {audio_file_name}")
    print("Successful conversion")
    
    return audio_file_name
def subtitle():
    try:
        file_name = video_to_audio()
        if not file_name:
            return
        
        base_url = "https://api.assemblyai.com/v2"
        headers = {
            "authorization": "" # Get your API from https://www.assemblyai.com/app after Sign up , add your API in here 
        }
        
        print("_"*20+"TRANSLATE"+"_"*20)
        print("Started translate....")
        with open(file_name, "rb") as f:
            calc_size = len(f.read())
            print(f"File size: {(calc_size) * 0.000001:.2f}MB")
        
        print("Wait for uploading....")
        with open(file_name, "rb") as f:
            response = requests.post(base_url + "/upload", headers=headers, data=f)
        
        upload_url = response.json()["upload_url"]
        data = {"audio_url": upload_url}
        url = base_url + "/transcript"
        response = requests.post(url, json=data, headers=headers)
        transcript_id = response.json()['id']
        polling_endpoint = f"{base_url}/transcript/{transcript_id}"
        print("Successful uploading progress 75%....")
        print("Please wait, the file is being processed...")

        while True:
            transcription_result = requests.get(polling_endpoint, headers=headers).json()
            if transcription_result['status'] == 'completed':
                print("Progress 95%")
                break
            elif transcription_result['status'] == 'error':
                raise RuntimeError(f"Transcription failed: {transcription_result['error']}")
            else:
                time.sleep(3)

        subtitle_text = get_subtitle_file(transcript_id, "srt")
        subtitle_file = "subtitles.srt"
        with open(subtitle_file, 'w') as w:
            w.write(subtitle_text)
        print(f"{subtitle_file} download successful")

    except FileNotFoundError as file_error:
        print("-" * 40)
        print(f"{file_error}")
        print("-" * 40)
    except TimeoutError as time_error:
        print(f"->{time_error}")
    except ValueError as v_error:
        print(f"->{v_error}")

def get_subtitle_file(transcript_id, file_format):
    if file_format not in ["srt", "vtt"]:
        raise ValueError("Invalid file format. Valid formats are 'srt' and 'vtt'.")

    url = f"https://api.assemblyai.com/v2/transcript/{transcript_id}/{file_format}"
    response = requests.get(url, headers={"authorization": "2ba819026c704d648dced28f3f52406f"})

    if response.status_code == 200:
        return response.text
    else:
        raise RuntimeError(f"Failed to retrieve {file_format.upper()} file: {response.status_code} {response.reason}")

# Call the translate function
subtitle()
