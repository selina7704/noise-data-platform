import streamlit as st
import requests
import numpy as np
import pandas as pd
import os
import time
import tensorflow as tf
from tensorflow.keras.models import load_model, Model
from tensorflow.keras.layers import Dense
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score, f1_score
import seaborn as sns
import matplotlib.pyplot as plt
import logging
from gtts import gTTS
import base64
import smtplib
from email.mime.text import MIMEText

class NoiseModel_page:
    def noisemodel_page(self):
        
        tab1, tab2= st.tabs(['소음 분류기', '알람 기준 설정'])
        
        FASTAPI_URL = "http://15.168.145.74:8008/predict"  # FastAPI 서버의 URL
       # 소음 분류기'
        with tab1:
            
            st.markdown("## 가이드 작성")
            
            # 저장 디렉토리
            upload_folder = "uploads"
            audio_save_path = "recorded_audio"
            os.makedirs(upload_folder, exist_ok=True)
            os.makedirs(audio_save_path, exist_ok=True)

                        # CSV용 전역 변수
            MODEL = None
            LOGITS_MODEL = None
            ENERGY_THRESHOLD = None  # 동적 계산
            CONFIDENCE_THRESHOLD = 0.99
            TEMPERATURE = 1.0
            MEAN_ENERGY_IND = -15.3398  # 초기값
            STD_ENERGY_IND = 8.2265     # 초기값

            # 라벨 정의
            label_dict = {'이륜차경적': 0, '이륜차주행음': 1, '차량경적': 2, '차량사이렌': 3, '차량주행음': 4, '기타소음': 5}
            reverse_label_dict = {v: k for k, v in label_dict.items()}
            english_labels = ['Motorcycle Horn', 'Motorcycle Running Sound', 'Vehicle Horn', 'Vehicle Siren', 'Vehicle Driving', 'Other Noise']
            unknown_label_index = label_dict['기타소음']
            
            tf.config.run_functions_eagerly(True)
            
            # 세션 상태 초기화
            if 'stop_audio' not in st.session_state:
                st.session_state['stop_audio'] = False

            # TTS 음성 알림 생성 함수
            def generate_tts(text, filename="alert.wav"):
                tts = gTTS(text=text, lang='ko', slow=False)
                tts.save(filename)
                return filename

            # 오디오 자동 재생 컴포넌트
            def autoplay_audio(file_path):
                with open(file_path, "rb") as f:
                    data = f.read()
                    b64 = base64.b64encode(data).decode()
                    audio_html = f"""
                        <audio autoplay src="data:audio/wav;base64,{b64}" type="audio/wav"></audio>
                    """
                    st.markdown(audio_html, unsafe_allow_html=True)
                    
            # 이메일 알림
            def send_email(to_email, subject, message):
                smtp_server = "smtp.gmail.com"
                smtp_port = 587 #465
                sender_email = "itmomdan0328@gmail.com"  # 자신의 Gmail 주소
                sender_password = "dhvfbjqqhkxlkhzt" #os.environ.get("dhvfbjqqhkxlkhzt")  # 앱 비밀번호 사용 (구글 계정 보안 설정 필요)

                msg = MIMEText(message)
                msg['Subject'] = subject
                msg['From'] = sender_email
                msg['To'] = to_email

                try:
                    server = smtplib.SMTP(smtp_server, smtp_port)
                    server.starttls()
                    server.login(sender_email, sender_password)
                    server.sendmail(sender_email, to_email, msg.as_string())
                    server.quit()
                    print("✅ 이메일 전송 완료!")
                except smtplib.SMTPAuthenticationError as e:
                    print(f"❌ 이메일 전송 실패: 인증 오류 - {e}")
                except smtplib.SMTPException as e:
                    print(f"❌ 이메일 전송 실패: SMTP 오류 - {e}")
                except Exception as e:
                    print(f"❌ 이메일 전송 실패: 기타 오류 - {e}")
                    
            # 경고 메시지 + 음성 알림 통합 함수
            def show_alert(message, level="warning"):
                color = "#ffcc00" if level == "warning" else "#ff4d4d"
                text_color = "black" if level == "warning" else "white"
                icon = "⚠️" if level == "warning" else "🚨"
                
                st.markdown(
                    f"""
                    <style>
                    @keyframes blink {{
                        0% {{ background-color: {color}; }}
                        50% {{ background-color: transparent; }}
                        100% {{ background-color: {color}; }}
                    }}
                    .blink-alert {{
                        animation: blink 1s linear infinite;
                        padding: 25px;
                        border-radius: 15px;
                        text-align: center;
                        color: {text_color};
                        font-size: 1.5em;
                        margin: 20px 0;
                    }}
                    </style>
                    <div class="blink-alert">
                        {icon} {message} {icon}
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
                
                if not st.session_state['stop_audio']:
                    alert_sound = generate_tts(message)
                    autoplay_audio(alert_sound)
                    os.remove(alert_sound)
                    time.sleep(3)


            # 예측 결과 처리 함수
            def process_prediction(response):
                if response.status_code == 200:
                    result = response.json()
                    if "error" in result:
                        show_alert("오디오 분석에 실패했습니다", "danger")
                        return
                    
                    # 종료 시간 기록 및 시간 계산
                    end_time = time.time()
                    elapsed_time = end_time - st.session_state['start_time']

                    st.write(f"🔊 **예측된 소음 유형:** {result.get('prediction', '알 수 없음')}")
                    st.write(f"📊 **Peak SPL (dB):** {result.get('spl_peak', 'N/A')}")
                    st.write(f"📊 **RMS SPL (dB):** {result.get('spl_rms', 'N/A')}")
                    st.write(f"📏 **추정 거리:** {result.get('estimated_distance', 'N/A')} 미터")
                    st.write(f"📡 **방향:** {result.get('direction', '알 수 없음')}")

                    # 경과 시간 출력
                    st.write(f"⏱️ **예측 소요 시간:** {elapsed_time:.2f} 초")

                    noise_type = result.get('prediction', '알 수 없음')
                    spl = result.get('spl_peak', 0)
                    distance = result.get('estimated_distance', 'N/A')
                    direction = result.get('direction', '알 수 없음')

                    if spl >= 70:
                        show_alert("위험 수준 소음 감지! 즉시 조치가 필요합니다", "danger")
                        alert_message = f"🚨위험 수준 소음 감지!🚨 소음 유형: {noise_type}, 강도: {spl}dB, 위치: {distance}m, 방향: {direction}"
                        send_email("itmomdan0328@gmail.com", "소음 경고", alert_message) # 이메일 기능 필요 시 주석 해제
                    elif spl >= 50:
                        show_alert("주의 요함: 지속적 노출 위험", "warning")
                        alert_message = f"⚠️주의 요함!⚠️ 소음 유형: {noise_type}, 강도: {spl}dB, 위치: {distance}m, 방향: {direction}"
                        send_email("itmomdan0328@gmail.com", "소음 경고", alert_message) # 이메일 기능 필요 시 주석 해제
                    
                    if not st.session_state['stop_audio']:
                        info_text = f"소음 유형은 {noise_type}입니다. 현재 소음 강도는 {spl} 데시벨로 측정되었으며, 약 {distance} 미터 거리에서 발생하고 있습니다."
                        info_sound = generate_tts(info_text)
                        autoplay_audio(info_sound)
                        os.remove(info_sound)
                else:
                    show_alert("서버 연결 오류 발생", "danger")
                    
                    
            # 녹음과 예측 처리
            
            st.subheader('소음 분류기')
            st.write(' ')
                    
            # 실시간 녹음 섹션
            with st.expander("🎙 녹음 방식", expanded=True):
                st.subheader("1. 배경 소음 녹음")
                background_audio = st.audio_input("배경 소음을 녹음하세요 (5초 권장)")
                background_path = os.path.join(audio_save_path, "background_audio.wav")
            
                if background_audio:
                    st.session_state['background_audio'] = background_audio  # 세션 상태에 저장
                    with open(background_path, "wb") as f:
                        f.write(background_audio.getvalue())
                    st.success(f"📂 배경 소음이 저장되었습니다: {background_path}")
                else:
                    st.session_state['background_audio'] = None  # 초기화

                st.subheader("2. 실제 소음 녹음")
                audio_data = st.audio_input("목표 소음을 녹음하세요")

                if audio_data:
                    file_path = os.path.join(audio_save_path, "recorded_audio.wav")
                    with open(file_path, "wb") as f:
                        f.write(audio_data.getvalue())
                    st.success(f"📂 녹음된 오디오가 저장되었습니다: {file_path}")

                    if st.button("녹음 데이터 분석"):
                        st.session_state['start_time'] = time.time()  # 시작 시간 기록 (세션 상태에 저장)
                        with st.spinner("분석 진행 중..."):
                            files = {"file": ("recorded_audio.wav", audio_data.getvalue(), "audio/wav")}
                            # 배경 소음 파일 전송 부분
                            if st.session_state['background_audio']:
                                files["background"] = (
                                    "background_audio.wav",
                                    st.session_state['background_audio'].getvalue(),
                                    "audio/wav",
                                )
                            response = requests.post(FASTAPI_URL, files=files)
                            process_prediction(response)  # process_prediction에서 시간 측정


            # 파일 업로드 섹션
            with st.expander("📁 파일 업로드 방식", expanded=True):
            # 기존 배경 소음 초기화
                st.session_state['background_audio'] = None

                uploaded_file = st.file_uploader("음성 파일을 업로드하세요", type=["wav"])
            
                if uploaded_file is not None:
                    st.audio(uploaded_file, format='audio/wav')
                    st.write(f"파일 이름: {uploaded_file.name}")

                    upload_path = os.path.join(upload_folder, uploaded_file.name)
                    with open(upload_path, "wb") as f:
                        f.write(uploaded_file.getvalue())
                    st.success(f"📂 업로드된 파일이 저장되었습니다: {upload_path}")
                    
                    if st.button("음성 예측하기"):
                        st.session_state['start_time'] = time.time()  # 시작 시간 기록 (세션 상태에 저장)
                        with st.spinner("분석 중..."):
                            response = requests.post(FASTAPI_URL, files={"file": uploaded_file})
                            process_prediction(response)  # process_prediction에서 시간 측정
                        
            
            # Stop Audio 버튼
            st.session_state['stop_audio'] = st.button("🛑 Stop Audio")
                

            



        # 알람 기준 설정
        with tab2:
            st.subheader('알람 기준 설정')
            
            
if __name__ == '__main__':
    m = NoiseModel_page()
    m.noisemodel_page()
