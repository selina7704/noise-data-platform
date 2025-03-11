import streamlit as st
import requests
import os
import time
import streamlit.components.v1 as components

# FastAPI 서버 주소
FASTAPI_URL = "http://localhost:8000/predict/"

# 저장할 디렉토리 생성
upload_folder = "uploads"  # 업로드한 파일 저장 폴더
audio_save_path = "recorded_audio"  # 녹음된 파일 저장 폴더
os.makedirs(upload_folder, exist_ok=True)
os.makedirs(audio_save_path, exist_ok=True)


# 경고 메시지 표시 함수 (CSS 애니메이션 추가)
def show_alert(message, level="warning"):
    color = "#ffcc00" if level == "warning" else "#ff4d4d"
    text_color = "black" if level == "warning" else "white"
    icon = "⚠️" if level == "warning" else "🚨"

    st.markdown(
        f"""
        <style>
        @keyframes blink {{
            0% {{ background-color: {color}; }}
            50% {{ background-color: white; }}
            100% {{ background-color: {color}; }}
        }}
        .blink {{
            animation: blink 1s linear infinite;
            padding: 35px;
            border-radius: 15px;
            text-align: center;
            color: {text_color};
            font-size: 29px;
            font-weight: bold;
        }}
        </style>
        <div class="blink">
            {icon} {message} {icon}
        </div>
        """,
        unsafe_allow_html=True,
    )

# FastAPI 응답 처리 함수
def process_prediction_response(response):
    """FastAPI 서버에서 받은 응답을 처리하고 결과를 출력합니다."""
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
                show_alert("소음이 매우 큽니다! 즉시 조치가 필요합니다.", level="danger")
            elif spl >= 50:
                show_alert("소음이 다소 큽니다. 주의하세요!", level="warning")
    else:
        st.error("❌ 서버와의 통신 오류 발생!")

def main():
    st.title("🔊 소음 분류기")

    animation_html = """
    <script>
        document.body.style.transition = "background-color 2s";
        document.body.style.backgroundColor = "#ffcc00";
        setTimeout(() => {
            document.body.style.backgroundColor = "white";
        }, 2000);
    </script>
    """
    components.html(animation_html, height=0)

    # 파일 업로드 섹션
    st.subheader("📂 음성 파일 업로드")
    uploaded_file = st.file_uploader("음성 파일을 업로드하세요", type=["wav"])

    if uploaded_file is not None:
        st.audio(uploaded_file, format='audio/wav')
        st.write(f"파일 이름: {uploaded_file.name}")

        # 파일 저장
        upload_path = os.path.join(upload_folder, uploaded_file.name)
        with open(upload_path, "wb") as f:
            f.write(uploaded_file.getvalue())

        st.success(f"📂 업로드된 파일이 저장되었습니다: {upload_path}")

        if st.button('🔍 업로드된 파일 예측하기'):
            start_time = time.time()
            files = {"file": (uploaded_file.name, uploaded_file.getvalue(), "audio/wav")}
            response = requests.post(FASTAPI_URL, files=files)
            elapsed_time = time.time() - start_time

            process_prediction_response(response)
            st.write(f"⏱️ 예측 소요 시간: {elapsed_time:.2f}초")

    # 오디오 녹음 섹션
    st.subheader("🎙️ 음성 녹음")
    audio_value = st.audio_input("음성을 녹음하세요")

    if audio_value:
        st.audio(audio_value, format='audio/wav')  # 녹음된 오디오 재생

        # 저장할 파일 경로 설정
        file_path = os.path.join(audio_save_path, "recorded_audio.wav")

        # 파일 저장
        with open(file_path, "wb") as f:
            f.write(audio_value.getvalue())

        st.success(f"📂 녹음된 오디오가 저장되었습니다: {file_path}")

        if st.button('🔍 녹음된 파일 예측하기'):
            start_time = time.time()
            
            # 녹음된 오디오 파일을 FastAPI 서버로 전송하여 예측 수행
            files = {"file": ("recorded_audio.wav", audio_value.getvalue(), "audio/wav")}
            response = requests.post(FASTAPI_URL, files=files)
            
            elapsed_time = time.time() - start_time

            process_prediction_response(response)
            st.write(f"⏱️ 예측 소요 시간: {elapsed_time:.2f}초")

if __name__ == "__main__":
    main()

