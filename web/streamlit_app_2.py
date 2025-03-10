import streamlit as st
import requests

# FastAPI 서버 주소
FASTAPI_URL = "http://localhost:8503/predict/"

def main():
    st.title("🔊 소음 분석 웹앱")
    st.write("WAV 파일을 업로드하면 소음 유형, 데시벨, 거리, 방향을 분석합니다.")

    # 파일 업로드
    uploaded_file = st.file_uploader("소음 파일을 업로드하세요 (WAV 형식)", type=["wav"])

    if uploaded_file is not None:
        st.audio(uploaded_file, format='audio/wav')
        st.write(f"파일 이름: {uploaded_file.name}")

        if st.button('🔍 소음 분석 실행'):
            files = {"file": (uploaded_file.name, uploaded_file.getvalue(), "audio/wav")}
            response = requests.post(FASTAPI_URL, files=files)

            if response.status_code == 200:
                prediction = response.json()
                if "error" in prediction:
                    st.error("오디오 분석 중 오류 발생! 🚨")
                else:
                    st.success("분석 완료 ✅")
                    st.write(f"**예측된 소음 유형:** {prediction.get('prediction', '알 수 없음')}")
                    st.write(f"**소음 크기 (dB):** {prediction.get('spl', 'N/A')} dB")
                    st.write(f"**추정 거리:** {prediction.get('estimated_distance', 'N/A')} 미터")
                    st.write(f"**방향:** {prediction.get('direction', '알 수 없음')}")
            else:
                st.error("서버와의 통신 오류 발생! ❌")

if __name__ == "__main__":
    main()

