import pyaudio

p = pyaudio.PyAudio()

print("Available Host APIs:\n")
for i in range(p.get_host_api_count()):
    info = p.get_host_api_info_by_index(i)
    print(f"{i}: {info['name']}  (default input device index: {info['defaultInputDevice']})")

print("\n----------------------------------------")
print("Trying to find and use WASAPI...\n")

wasapi_index = None
for i in range(p.get_host_api_count()):
    info = p.get_host_api_info_by_index(i)
    if "WASAPI" in info["name"]:
        wasapi_index = i
        break

if wasapi_index is None:
    print("WASAPI not found on this system.")
else:
    host_info = p.get_host_api_info_by_index(wasapi_index)
    default_device = host_info["defaultInputDevice"]
    print(f"WASAPI default input device index: {default_device}")

    if default_device == -1:
        print("No default input device set for WASAPI.")
    else:
        device_info = p.get_device_info_by_index(default_device)
        print("Device info:", device_info)

        try:
            stream = p.open(
                format=pyaudio.paInt16,
                channels=int(device_info["maxInputChannels"]),
                rate=int(device_info["defaultSampleRate"]),
                input=True,
                input_device_index=default_device,
                frames_per_buffer=1024,
                start=False,
            )
            stream.start_stream()
            data = stream.read(1024, exception_on_overflow=False)
            stream.stop_stream()
            stream.close()
            print("\n[SUCCESS] WASAPI microphone works!")
        except Exception as e:
            print(f"\n[FAILS] WASAPI also failed: {e}")

p.terminate()