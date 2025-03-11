
import streamlit as st
import requests
import os 
import time 
import sounddevice as sd
import numpy as np
import wave

# FastAPI 서버 주소
FASTAPI_URL = "http://localhost:8000/predict/"

# 저장할 디렉토리 생성
upload_folder = "uploads"  # 업로드한 파일 저장 폴더
audio_save_path = "recorded_audio"  # 녹음된 파일 저장 폴더
os.makedirs(upload_folder, exist_ok=True)
os.makedirs(audio_save_path, exist_ok=True)

# 경고 메시지 표시 함수
def show_alert(message, level="warning"):
    if level == "danger":
        st.markdown(
            f"""
            <div style="background-color:#ff4d4d; padding:15px; border-radius:10px; text-align:center;">
                <h2 style="color:white;">🚨 경고! {message} 🚨</h2>
            </div>
            """,
            unsafe_allow_html=True,
        )
    elif level == "warning":
        st.markdown(
            f"""
            <div style="background-color:#ffcc00; padding:15px; border-radius:10px; text-align:center;">
                <h2 style="color:black;">⚠️ 주의! {message} ⚠️</h2>
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        st.success(message)

# 오디오 녹음 함수
def record_audio(filename, duration=5, samplerate=44100):
    st.write("🎤 녹음 중...")
    recording = sd.rec(int(duration * samplerate), samplerate=samplerate, channels=1, dtype=np.int16)
    sd.wait()
    
    filepath = os.path.join(audio_save_path, filename)
    with wave.open(filepath, 'wb') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(samplerate)
        wf.writeframes(recording.tobytes())
    
    st.success(f"✅ 녹음이 완료되었습니다: {filepath}")
    return filepath

def main():
    st.title("🔊 소음 분류기")

    # 파일 업로드
    uploaded_file = st.file_uploader("📂 음성 파일을 업로드하세요", type=["wav"])

    # 녹음 버튼
    if st.button("🎙️ 녹음 시작 (5초)"):
        recorded_file = record_audio("recorded.wav")
        st.audio(recorded_file, format='audio/wav')
        uploaded_file = recorded_file  # 녹음 파일을 업로드 파일 변수로 설정

    if uploaded_file is not None:
        st.audio(uploaded_file, format='audio/wav')  
        st.write(f"파일 이름: {uploaded_file if isinstance(uploaded_file, str) else uploaded_file.name}")
        
        # 파일 저장
        if isinstance(uploaded_file, str):
            upload_path = uploaded_file  # 녹음된 파일 경로 유지
        else:
            upload_path = os.path.join(upload_folder, uploaded_file.name)
            with open(upload_path, "wb") as f:
                f.write(uploaded_file.getvalue())

        st.success(f"📂 업로드된 파일이 저장되었습니다: {upload_path}")

        if st.button('🔍 예측하기'):
            start_time = time.time()
            with open(upload_path, "rb") as f:
                files = {"file": (os.path.basename(upload_path), f, "audio/wav")}
                response = requests.post(FASTAPI_URL, files=files)
            elapsed_time = time.time() - start_time

            if response.status_code == 200:
                prediction = response.json()
                if "error" in prediction:
                    st.error("🚨 오디오 분석 중 오류 발생!")
                else:
                    st.success("✅ 분석 완료!")
                    st.write(f"**예측된 소음 유형:** {prediction.get('prediction', '알 수 없음')}")
                    spl = prediction.get('spl', 0)
                    st.write(f"**소음 크기:** {spl} dB")
                    st.write(f"**추정 거리:** {prediction.get('estimated_distance', 'N/A')} 미터")
                    st.write(f"**방향:** {prediction.get('direction', '알 수 없음')}")

                    # 소음 강도에 따른 경고 표시
                    if spl >= 70:
                        show_alert("소음이 매우 큽니다!\n즉시 조치가 필요합니다.", level="danger")
                    elif spl >= 50:
                        show_alert("소음이 다소 큽니다.\n주의하세요!", level="warning")
            else:
                st.error("❌ 서버와의 통신 오류 발생!")

if __name__ == "__main__":
    main()
