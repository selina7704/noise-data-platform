import pyaudio

p = pyaudio.PyAudio()

# 모든 입력 장치 정보 출력
for i in range(p.get_device_count()):
    info = p.get_device_info_by_index(i)
    if info.get('maxInputChannels') > 0:
        print(f"Device {i}: {info.get('name')}")

# 사용하려는 장치 인덱스 입력
input_device_index = 1  # 예시: 인덱스 1번 장치 사용

stream = p.open(format=pyaudio.paInt16,
                channels=1,
                rate=44100,
                input=True,
                input_device_index=input_device_index,
                frames_per_buffer=1024)