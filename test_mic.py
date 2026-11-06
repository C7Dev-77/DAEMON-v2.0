import speech_recognition as sr

# Show all microphones
for i, name in enumerate(sr.Microphone.list_microphone_names()):
    print(f"{i}: {name}")

recognizer = sr.Recognizer()

# Change this number after seeing the list
mic = sr.Microphone(device_index=1)

with mic as source:
    print("\nSpeak now...")
    recognizer.adjust_for_ambient_noise(source, duration=1)
    audio = recognizer.listen(source)

try:
    text = recognizer.recognize_google(audio)
    print("You said:", text)
except Exception as e:
    print("Error:", e)