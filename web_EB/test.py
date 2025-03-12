import pyaudio
import wave

# PyAudio 설정
p = pyaudio.PyAudio()

try:
    # 마이크로부터 오디오 입력 받기
    stream = p.open(format=pyaudio.paInt16,
                    channels=1,
                    rate=44100,
                    input=True,
                    frames_per_buffer=1024)

    print("Recording...")

    # 5초간 오디오를 녹음하고, 녹음된 데이터를 저장
    frames = []
    for i in range(0, int(44100 / 1024 * 5)):  # 5초 녹음
        data = stream.read(1024)
        frames.append(data)

    print("Finished recording.")

    # 녹음된 데이터 저장
    stream.stop_stream()
    stream.close()

    # 녹음된 데이터를 wave 파일로 저장
    wf = wave.open("test_output.wav", 'wb')
    wf.setnchannels(1)  # 채널 수
    wf.setsampwidth(p.get_sample_size(pyaudio.paInt16))  # 샘플 폭
    wf.setframerate(44100)  # 샘플링 주파수
    wf.writeframes(b''.join(frames))  # 녹음된 데이터를 파일에 작성
    wf.close()

    print("File saved as test_output.wav")

except Exception as e:
    print(f"Error: {e}")

finally:
    p.terminate()