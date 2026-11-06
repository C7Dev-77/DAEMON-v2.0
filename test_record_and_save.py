import speech_recognition as sr
import pyaudio

p = pyaudio.PyAudio()
wasapi_index = None
for i in range(p.get_host_api_count()):
    info = p.get_host_api_info_by_index(i)
    if "WASAPI" in info["name"]:
        wasapi_index = i
        break

mic_device_index = p.get_host_api_info_by_index(wasapi_index)["defaultInputDevice"]
device_info = p.get_device_info_by_index(mic_device_index)
native_rate = int(device_info["defaultSampleRate"])
p.terminate()

print(f"Using device: {device_info['name']}")
print(f"Native sample rate: {native_rate}")

recognizer = sr.Recognizer()

print("\nSpeak clearly for 4 seconds after 'Recording...' appears.")

with sr.Microphone(device_index=mic_device_index, sample_rate=native_rate, chunk_size=1024) as source:
    recognizer.adjust_for_ambient_noise(source, duration=1)
    print("Recording...")
    audio = recognizer.record(source, duration=4)

with open("test_recording.wav", "wb") as f:
    f.write(audio.get_wav_data())

print("Saved to test_recording.wav — play this file and confirm you can hear your voice clearly.")

try:
    text = recognizer.recognize_google(audio)
    print("Google understood:", text)
except sr.UnknownValueError:
    print("Google could not understand the audio.")
except sr.RequestError as e:
    print("Google service error:", e)