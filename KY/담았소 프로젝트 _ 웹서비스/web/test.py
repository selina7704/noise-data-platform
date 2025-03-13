import streamlit as st
import os

# 저장할 디렉토리 생성
audio_save_path = "recorded_audio"
os.makedirs(audio_save_path, exist_ok=True)

st.title("🎙️ 음성 녹음 테스트")

# 사용자 오디오 입력 받기
audio_value = st.audio_input("음성을 녹음하세요!")

if audio_value:
    st.audio(audio_value, format='audio/wav')  # 녹음된 오디오 재생
    
    # 저장할 파일 경로 설정
    file_path = os.path.join(audio_save_path, "recorded_audio.wav")
    
    # 파일 저장
    with open(file_path, "wb") as f:
        f.write(audio_value.getvalue())
    
    st.success(f"✅ 녹음된 오디오가 저장되었습니다: {file_path}")
