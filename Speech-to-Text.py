import requests
import time
from tkinter import filedialog
import moviepy.editor
from datetime import datetime
def video_to_audio():
    print("_" * 26 + "CONVERT" + "_" * 26)
    print("Select Video to convert it to Audio file for best subtitle")
    video_name = filedialog.askopenfilename(
        title="Select Video",
        filetypes=[("Video Files", "*.mp4;*.wmv;*.mov;*.mkv;*.H.264")]
    )
    if not video_name:
        print("No file selected.")
        return None

    with open(video_name, "rb") as file:
        video_size = len(file.read())
        print(f"Video size: {(video_size) * 0.000001:.2f}MB")

    video = moviepy.editor.VideoFileClip(video_name)
    print("Video uploaded...")
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    audio_file_name = f"audio_{timestamp}.mp3"
    audio = video.audio
    audio.write_audiofile(audio_file_name)

    with open(audio_file_name, "rb") as f:
        audio_size = len(f.read())
        print(f"Audio file size: {(audio_size) * 0.000001:.2f}MB")
    print(f"Audio file name: {audio_file_name}")
    print("Successful conversion")
    
    return audio_file_name


def Transcription():
    try:
        file_name = video_to_audio()
        if file_name is None:
            return
        
        base_url = "https://api.assemblyai.com/v2"
        headers = {"authorization": ""} # add Your API key here
        print("Started....")

        with open(file_name, "rb") as f:
            calc_size = len(f.read())
            print(f"File size: {(calc_size) * 0.000001:.2f}MB")
        
        print("Wait for uploading....")
        with open(file_name, "rb") as f:
            response = requests.post(base_url + "/upload", headers=headers, data=f)
        
        upload_url = response.json()["upload_url"]
        data = {"audio_url": upload_url}
        response = requests.post(base_url + "/transcript", json=data, headers=headers)
        transcript_id = response.json()['id']
        polling_endpoint = f"https://api.assemblyai.com/v2/transcript/{transcript_id}"
        print("Successful uploading, progress 75%....")
        print("Please wait a moment...")
        
        while True:
            transcription_result = requests.get(polling_endpoint, headers=headers).json()

            if transcription_result['status'] == 'completed':
                print("Progress 95%")
                print("Transcription completed")
                break
            elif transcription_result['status'] == 'error':
                raise RuntimeError(f"Transcription failed: {transcription_result['error']}")
            else:
                print("Transcription in progress...")
                time.sleep(10)

        def get_subtitle_file(transcript_id, file_format, headers):
            if file_format not in ["srt", "vtt"]:
                raise ValueError("Invalid file format. Valid formats are 'srt' and 'vtt'.")

            url = f"https://api.assemblyai.com/v2/transcript/{transcript_id}/{file_format}"

            response = requests.get(url, headers=headers)

            if response.status_code == 200:
                return response.text
            else:
                raise RuntimeError(f"Failed to retrieve {file_format.upper()} file: {response.status_code} {response.reason}")

        def save_subtitle_file():
            # Loop until valid file format is provided
            while True:
                file_format = input("What file format do you need (srt/vtt): ").strip().lower()
                if file_format in ["srt", "vtt"]:
                    subtitle_text = get_subtitle_file(transcript_id, file_format, headers)
                    subtitle_file = input(f"Enter the desired output file name (without extension): ").strip()
                    if not subtitle_file.lower().endswith(f'.{file_format}'):
                        subtitle_file += f'.{file_format}'
                    
                    with open(subtitle_file, 'w') as f:
                        f.write(subtitle_text)
                    print(f"{subtitle_file} Download successful")
                    break
                else:
                    print("Please enter file format srt or vtt!")
        save_subtitle_file()
        
    except TimeoutError as time_error:
        print(f"->{time_error}")
    except ValueError as v_error:
        print(f"->{v_error}")
    except RuntimeError as r_error:
        print(f"->{r_error}")

# Run the Transcription function
Transcription()
