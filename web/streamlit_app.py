import streamlit as st
import requests
import numpy as np
import librosa
import io
import pyaudio

# FastAPI 서버 주소
FASTAPI_URL = "http://localhost:8000/predict/"

# 실시간 음성 녹음 설정
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 22050
CHUNK = 1024
RECORD_SECONDS = 5


# 실시간 녹음 함수
def record_audio():
    p = pyaudio.PyAudio()
    stream = p.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    frames_per_buffer=CHUNK)
    
    frames = []
    for _ in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
        data = stream.read(CHUNK)
        frames.append(data)
    
    stream.stop_stream()
    stream.close()
    p.terminate()
    
    # 녹음된 오디오 데이터를 numpy 배열로 변환
    audio_data = np.frombuffer(b''.join(frames), dtype=np.int16)
    return audio_data




def main():
    st.title("소음 분류기")

    # 파일 업로드
    uploaded_file = st.file_uploader("음성 파일을 업로드하세요", type=["wav"])

    if uploaded_file is not None:
        st.audio(uploaded_file, format='audio/wav')  # 업로드한 파일을 웹에서 들을 수 있게 표시
        st.write(f"파일 이름: {uploaded_file.name}")

        # 예측 버튼 클릭 시 예측 수행
        if st.button('예측하기'):
            # 파일을 FastAPI 서버로 전송
            files = {"file": (uploaded_file.name, uploaded_file.getvalue(), "audio/wav")}
            response = requests.post(FASTAPI_URL, files=files)

            if response.status_code == 200:
                prediction = response.json().get("prediction")
                st.write(f"예측된 소음 유형: {prediction}")
            else:
                st.write("예측 실패. 다시 시도해 주세요.")
                
    # 실시간 음성 녹음 기능
    if st.button("소음 예측 시작 (실시간 녹음)"):
        st.write("녹음을 시작합니다... 5초 동안 녹음 후 예측합니다.")
        
        # 실시간 녹음
        audio_data = record_audio()
        
        # 음성을 FastAPI 서버로 전송
        audio_data_io = io.BytesIO()
        librosa.output.write_wav(audio_data_io, audio_data, RATE)  # 녹음된 데이터를 BytesIO로 저장
        
        files = {"file": ("recorded.wav", audio_data_io.getvalue(), "audio/wav")}
        response = requests.post(FASTAPI_URL, files=files)
        
        if response.status_code == 200:
            prediction = response.json().get("prediction")
            st.write(f"예측된 소음 유형: {prediction}")
        else:
            st.write("예측 실패. 다시 시도해 주세요.")

if __name__ == "__main__":
    main()
