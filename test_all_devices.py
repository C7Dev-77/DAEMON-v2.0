import pyaudio

p = pyaudio.PyAudio()

print("Testing all input-capable devices...\n")

working = []

for i in range(p.get_device_count()):
    info = p.get_device_info_by_index(i)
    if info["maxInputChannels"] > 0:
        name = info["name"]
        try:
            stream = p.open(
                format=pyaudio.paInt16,
                channels=1,
                rate=44100,
                input=True,
                input_device_index=i,
                frames_per_buffer=1024,
                start=False,
            )
            stream.start_stream()
            data = stream.read(1024, exception_on_overflow=False)
            stream.stop_stream()
            stream.close()
            print(f"[WORKS]  index {i}: {name}")
            working.append(i)
        except Exception as e:
            print(f"[FAILS]  index {i}: {name}  -->  {e}")

p.terminate()

print("\n----------------------------------------")
if working:
    print("Working device indexes:", working)
else:
    print("No working input devices found.")
print("----------------------------------------")