import pyaudio

p = pyaudio.PyAudio()

device = p.get_device_info_by_index(1)  # Microphone Array (Realtek)

print(device)

stream = p.open(
    format=pyaudio.paInt16,
    channels=1,
    rate=44100,
    input=True,
    input_device_index=1,
    frames_per_buffer=1024,
    start=False,
)

print("Opened successfully!")

stream.start_stream()
print("Streaming...")

data = stream.read(1024, exception_on_overflow=False)

print("Read", len(data), "bytes")

stream.stop_stream()
stream.close()
p.terminate()