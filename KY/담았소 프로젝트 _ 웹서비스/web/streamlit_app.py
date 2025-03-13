import streamlit as st
import requests

FASTAPI_URL = "http://localhost:8001/predict/"

def main():
    st.title("🔊 소음 분석 웹앱")
    st.write("WAV 파일을 업로드하면 소음 유형, 데시벨, 거리, 방향을 분석합니다.")

    uploaded_file = st.file_uploader("소음 파일을 업로드하세요 (WAV 형식)", type=["wav"])

    if uploaded_file is not None:
        st.audio(uploaded_file, format='audio/wav')
        st.write(f"파일 이름: {uploaded_file.name}")

        if st.button('🔍 소음 분석 실행'):
            files = {"file": (uploaded_file.name, uploaded_file.getvalue(), "audio/wav")}
            response = requests.post(FASTAPI_URL, files=files)

            if response.status_code == 200:
                prediction = response.json()
                st.success("✅ 분석 완료!")

                st.write(f"🔊 **예측된 소음 유형:** {prediction.get('prediction', '알 수 없음')}")
                st.write(f"📊 **Peak SPL (dB):** {prediction.get('spl_peak', 'N/A')}")
                st.write(f"📊 **RMS SPL (dB):** {prediction.get('spl_rms', 'N/A')}")
                st.write(f"📏 **추정 거리:** {prediction.get('estimated_distance', 'N/A')} 미터")
                st.write(f"📡 **방향:** {prediction.get('direction', '알 수 없음')}")
            else:
                st.error("❌ 서버 오류 발생!")

if __name__ == "__main__":
    main()
