import sounddevice as sd
import numpy as np

# 샘플 레이트 (초당 샘플 개수)
samplerate = 44100
# 녹음 시간 (초 단위)
duration = 5  # 5초 녹음

# 녹음 함수
def record_audio(duration, samplerate):
    print("녹음 시작...")
    # 음성 녹음
    audio_data = sd.rec(int(duration * samplerate), samplerate=samplerate, channels=1, dtype='float32')
    sd.wait()  # 녹음이 끝날 때까지 기다림
    print("녹음 종료")
    return audio_data

# 녹음 후 바로 재생
def play_audio(audio_data, samplerate):
    print("재생 시작...")
    sd.play(audio_data, samplerate)
    sd.wait()  # 재생이 끝날 때까지 기다림
    print("재생 종료")

# 녹음하고 바로 재생
audio_data = record_audio(duration, samplerate)
play_audio(audio_data, samplerate)
