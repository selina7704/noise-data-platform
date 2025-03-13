# import streamlit as st
# import requests
# import os
# import time
# from gtts import gTTS
# import base64

# # FastAPI 서버 주소
# FASTAPI_URL = "http://localhost:8000/predict/"

# # 저장 디렉토리 설정
# upload_folder = "uploads"
# audio_save_path = "recorded_audio"
# os.makedirs(upload_folder, exist_ok=True)
# os.makedirs(audio_save_path, exist_ok=True)

# # TTS 음성 알림 생성 함수
# def generate_tts(text, filename="alert.mp3"):
#     tts = gTTS(text=text, lang='ko', slow=False)
#     tts.save(filename)
#     return filename

# # 오디오 자동 재생 컴포넌트
# def autoplay_audio(file_path):
#     with open(file_path, "rb") as f:
#         data = f.read()
#         b64 = base64.b64encode(data).decode()
#         audio_html = f"""
#             <audio autoplay>
#             <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
#             </audio>
#         """
#         st.markdown(audio_html, unsafe_allow_html=True)

# # 경고 메시지 + 음성 알림 통합 함수
# def show_alert(message, level="warning"):
#     # 시각적 경고
#     color = "#ffcc00" if level == "warning" else "#ff4d4d"
#     text_color = "black" if level == "warning" else "white"
#     icon = "⚠️" if level == "warning" else "🚨"
    
#     st.markdown(
#         f"""
#         <style>
#         @keyframes blink {{
#             0% {{ background-color: {color}; }}
#             50% {{ background-color: transparent; }}
#             100% {{ background-color: {color}; }}
#         }}
#         .blink-alert {{
#             animation: blink 1s linear infinite;
#             padding: 25px;
#             border-radius: 15px;
#             text-align: center;
#             color: {text_color};
#             font-size: 1.5em;
#             margin: 20px 0;
#         }}
#         </style>
#         <div class="blink-alert">
#             {icon} {message} {icon}
#         </div>
#         """,
#         unsafe_allow_html=True,
#     )
    
#     # 음성 알림
#     alert_sound = generate_tts(message)
#     autoplay_audio(alert_sound)
#     os.remove(alert_sound)  # 임시 파일 정리

# # 예측 결과 처리 함수
# def process_prediction(response):
#     if response.status_code == 200:
#         result = response.json()
#         if "error" in result:
#             show_alert("오디오 분석에 실패했습니다", "danger")
#             return
        
#         st.success("✅ 분석 결과")
#         st.write(f"**유형**: {result.get('prediction', '알 수 없음')}")
#         st.write(f"**소음 강도**: {result.get('spl', 0)} dB")
#         st.write(f"**추정 위치**: {result.get('estimated_distance', 'N/A')}m 방향")
        
#         # 음성 설명 자동 재생
#         tts_text = f"""소음 유형은 {result['prediction']}입니다. 
#         현재 소음 강도는 {result['spl']}데시벨로 측정되었으며, 
#         약 {result['estimated_distance']}미터 거리에서 발생하고 있습니다."""
#         info_sound = generate_tts(tts_text)
#         autoplay_audio(info_sound)
#         os.remove(info_sound)
        
#         # 위험도 평가
#         spl = result.get('spl', 0)
#         if spl >= 70:
#             show_alert("위험 수준 소음 감지! 즉시 조치가 필요합니다", "danger")
#         elif spl >= 50:
#             show_alert("주의 요함: 지속적 노출 위험", "warning")

#     else:
#         show_alert("서버 연결 오류 발생", "danger")

# # 메인 앱 인터페이스
# def main():
#     st.title("🔊 스마트 소음 감지 시스템")
#     st.markdown("**청각 지원 모드 활성화** 🦻")
    
#     # 파일 업로드 섹션
#     with st.expander("📁 파일 업로드 방식", expanded=True):
#         uploaded_file = st.file_uploader("WAV 파일 선택", type=["wav"])
#         if uploaded_file and st.button("업로드 파일 분석"):
#             with st.spinner("분석 중..."):
#                 # 파일 처리 및 분석 로직
#                 response = requests.post(FASTAPI_URL, files={"file": uploaded_file})
#                 process_prediction(response)
    
#     # 실시간 녹음 섹션
#     with st.expander("🎙 실시간 녹음 방식", expanded=True):
#         audio_data = st.audio_input("실시간 음성 입력")
#         if audio_data and st.button("녹음 데이터 분석"):
#             with st.spinner("실시간 분석 진행 중..."):
#                 # 녹음 데이터 처리
#                 response = requests.post(FASTAPI_URL, files={"file": audio_data})
#                 process_prediction(response)

# if __name__ == "__main__":
#     main()
