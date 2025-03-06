import streamlit as st
import requests
import numpy as np
import librosa
import io
import pyaudio
import os 

# FastAPI 서버 주소
FASTAPI_URL = "http://localhost:8000/predict/"


# 저장할 디렉토리 생성
audio_save_path = "recorded_audio"
os.makedirs(audio_save_path, exist_ok=True)


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
                result = response.json()
                prediction = result.get("prediction")
                distance = result.get("estimated_distance")
                direction = result.get("direction")
                alert = result.get("distance_alert")
                
                # 예측된 소음 유형과 분석 결과 출력
                st.write(f"예측된 소음 유형: {prediction}")
                st.write(f"추정 거리: {distance} 미터")
                st.write(f"추정 방향: {direction if direction else '알 수 없음'}")
                st.write(f"알람: {alert}")
            else:
                st.write("예측 실패. 다시 시도해 주세요.")
                
    # 사용자 오디오 입력 받기
    audio_value = st.audio_input("음성을 녹음하세요!")

    if audio_value:
        st.audio(audio_value, format='audio/wav')  # 녹음된 오디오 재생
        
        # 저장할 파일 경로 설정
        file_path = os.path.join(audio_save_path, "recorded_audio.wav")
        
        # 파일 저장
        with open(file_path, "wb") as f:
            f.write(audio_value.getvalue())
        
        st.success(f"녹음된 오디오가 저장되었습니다: {file_path}")

        # 녹음된 오디오 파일을 FastAPI 서버로 전송하여 예측 수행
        files = {"file": ("recorded_audio.wav", audio_value.getvalue(), "audio/wav")}
        response = requests.post(FASTAPI_URL, files=files)

        if response.status_code == 200:
            prediction = response.json().get("prediction")
            st.write(f"예측된 소음 유형: {prediction}")
        else:
            st.write("예측 실패. 다시 시도해 주세요.") 
        
        if response.status_code == 200:
            result = response.json()
            prediction = result.get("prediction")
            distance = result.get("estimated_distance")
            direction = result.get("direction")
            alert = result.get("distance_alert")
                
            # 예측된 소음 유형과 분석 결과 출력
            st.write(f"예측된 소음 유형: {prediction}")
            st.write(f"추정 거리: {distance} 미터")
            st.write(f"추정 방향: {direction if direction else '알 수 없음'}")
            st.write(f"알람: {alert}")
        else:
            st.write("예측 실패. 다시 시도해 주세요.")   
                 
if __name__ == "__main__":
    main()
