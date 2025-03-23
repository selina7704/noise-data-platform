import streamlit as st
import requests
import os
import time
from gtts import gTTS
import base64
import smtplib
from email.mime.text import MIMEText
import pandas as pd
from datetime import datetime
import mysql.connector
import config
from config import DB_CONFIG

# .env 로드 제거하고 config에서 직접 사용
sender_email = config.SENDER_EMAIL
sender_password = config.SENDER_PASSWORD

# 저장 디렉토리 설정
upload_folder = "uploads"
audio_save_path = "recorded_audio"
os.makedirs(upload_folder, exist_ok=True)
os.makedirs(audio_save_path, exist_ok=True)

# FastAPI 서버 주소
FASTAPI_URL = "http://15.168.145.74:8008/predict/"

# TTS 음성 생성 함수
def generate_tts(text, filename="alert.wav"):
    tts = gTTS(text=text, lang='ko', slow=False)
    tts.save(filename)
    return filename

# 오디오 자동 재생 함수
def autoplay_audio(file_path):
    with open(file_path, "rb") as f:
        data = f.read()
        b64 = base64.b64encode(data).decode()
        audio_html = f"""
            <audio autoplay src="data:audio/wav;base64,{b64}" type="audio/wav"></audio>
        """
        st.markdown(audio_html, unsafe_allow_html=True)

# 유저 정보 조회 함수 추가
def get_user_info(user_id):
    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor(dictionary=True)
    query = "SELECT id, name, guardian_email FROM users WHERE id = %s"
    cursor.execute(query, (user_id,))
    user = cursor.fetchone()
    conn.close()
    return user

# 이메일 발송 함수 (SOS 메일 포함)
def send_email(to_email, subject, message):
    smtp_server = "smtp.gmail.com"
    smtp_port = 587
    sender_email = config.SENDER_EMAIL
    sender_password = config.SENDER_PASSWORD

    if not sender_email or not sender_password:
        st.error("❌ SENDER_EMAIL 또는 SENDER_PASSWORD가 설정되지 않았습니다!")
        return False

    msg = MIMEText(message)
    msg['Subject'] = subject
    msg['From'] = sender_email
    msg['To'] = to_email

    try:
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.ehlo()
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, to_email, msg.as_string())
        server.quit()
        st.success("✅ 긴급 이메일이 전송되었습니다!")
        return True
    except smtplib.SMTPAuthenticationError:
        st.error("❌ 인증 오류: Gmail 앱 비밀번호가 잘못되었거나 계정 설정을 확인해주세요!")
        return False
    except smtplib.SMTPException as e:
        st.error(f"❌ SMTP 오류: {str(e)}")
        return False
    except Exception as e:
        st.error(f"❌ 기타 오류: {str(e)}")
        return False

def send_sos_email(user_id, result, latitude=None, longitude=None):
    user_info = get_user_info(user_id)
    if not user_info or not user_info.get('guardian_email'):
        st.error("❌ 보호자 이메일이 등록되지 않았습니다.")
        return False

    # 예측 결과에서 정보 추출
    noise_type = result.get('prediction', '알 수 없음')
    spl_peak = result.get('spl_peak', 0)
    spl_rms = result.get('spl_rms', 0)
    distance = result.get('estimated_distance', 'N/A')
    direction = result.get('direction', '알 수 없음')
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # 위치 정보 (추가 시 반영 가능)
    location = f"위도: {latitude}, 경도: {longitude}" if latitude and longitude else "위치 정보 없음"

    # 이메일 내용
    subject = "📢 긴급 SOS 알림"
    message = f"""
보호자님, 안녕하세요.

[{user_info['name']}]님이 위험 상황에 처해 있어 긴급 연락을 드립니다.

📍 위치: {location}
🔊 감지된 소음 유형: {noise_type}
📊 최대 소음 강도: {spl_peak} dB
📊 평균 소음 강도: {spl_rms} dB
📏 추정 거리: {distance} 미터
📡 방향: {direction}
⏰ 발생 시각: {timestamp}

⚠️ 즉시 확인이 필요합니다.

필요 시 즉시 연락 부탁드립니다.

감사합니다.
[Damasso Noise Platform]
"""
    return send_email(user_info['guardian_email'], subject, message)

# 경고 메시지 표시 함수
def show_alert(message, level="warning", play_tts=True):
    color = "#ffcc00" if level == "warning" else "#ff4d4d"
    text_color = "black" if level == "warning" else "white"
    icon = "⚠️" if level == "warning" else "🚨"
    
    st.markdown(
        f"""
        <div style='background-color: {color}; padding: 20px; border-radius: 10px; text-align: center; color: {text_color}; font-size: 1.3em; font-weight: bold; margin: 15px 0;'>
            {icon} {message} {icon}
        </div>
        """,
        unsafe_allow_html=True,
    )
    
    if play_tts and st.session_state['tts_enabled']:
        st.session_state['tts_queue'].append(message)

# 소음 강도 게이지 함수
def display_noise_gauge(label, value, max_value=120):
    if value <= 50:
        color = "#3498db"
    elif value <= 70:
        color = "#ffcc00"
    else:
        color = "#ff4d4d"
    
    st.write(f"{label}: {value} dB")
    st.markdown(
        f"""
        <div style="display: flex; align-items: center;">
            <span style="width: 30px; text-align: right; margin-right: 10px;">0</span>
            <div style="flex-grow: 1;">
                <progress value="{value}" max="{max_value}" style="width: 100%; height: 20px;">
                    <style>progress::-webkit-progress-value {{ background-color: {color}; }}</style>
                </progress>
            </div>
            <span style="width: 30px; text-align: left; margin-left: 10px;">{max_value}</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

# 예측 결과 표시 함수
def display_prediction_result(result, elapsed_time):
    st.markdown("### 📋 분석 결과", unsafe_allow_html=True)
    st.write(f"🔊 **예측된 소음 유형:** {result.get('prediction', '알 수 없음')}")
    spl_peak = result.get('spl_peak', 0)
    display_noise_gauge("📊 최대 소음 강도", spl_peak)
    spl_rms = result.get('spl_rms', 0)
    display_noise_gauge("📊 평균 소음 강도", spl_rms)
    st.write(f"📏 **추정 거리:** {result.get('estimated_distance', 'N/A')} 미터")
    st.write(f"📡 **방향:** {result.get('direction', '알 수 없음')}")
    st.write(f"⏱️ **분석 소요 시간:** {elapsed_time:.2f} 초")
    return spl_peak

# TTS 순차 재생 함수
def play_tts_queue():
    if 'tts_queue' in st.session_state and st.session_state['tts_queue']:
        for text in st.session_state['tts_queue']:
            tts_file = generate_tts(text)
            autoplay_audio(tts_file)
            os.remove(tts_file)
            time.sleep(5)  # TTS 간 5초 간격
        st.session_state['tts_queue'] = []

# 타이머 표시 함수 (SOS 메일 발송 포함)
def display_timer(start_time, user_id, result, duration=60):
    timer_container = st.empty()
    bar_container = st.empty()
    
    end_time = start_time + duration
    while time.time() < end_time:
        elapsed = time.time() - start_time
        remaining_time = max(duration - elapsed, 0)
        remaining_percentage = (remaining_time / duration) * 100
        
        with timer_container:
            st.write(f"남은 시간: {int(remaining_time // 60)}분 {int(remaining_time % 60)}초")
        with bar_container:
            st.progress(remaining_percentage / 100)
        
        time.sleep(1)
    
    if remaining_time <= 1 and not st.session_state['email_sent'] and st.session_state['sos_email_enabled']:
        send_sos_email(user_id, result)
        st.session_state['email_sent'] = True
        st.session_state['danger_alert_time'] = None
        timer_container.empty()
        bar_container.empty()

# 예측 결과 처리 함수 (user_id 추가)
def process_prediction(response, mode, user_id, audio_data=None, latitude=None, longitude=None):
    if response.status_code == 200:
        result = response.json()
        if "error" in result:
            show_alert("오디오 분석에 실패했습니다", "danger")
            return None, None, None
        
        end_time = time.time()
        elapsed_time = end_time - st.session_state['start_time']
        
        st.session_state[f'{mode}_result'] = result
        st.session_state[f'{mode}_elapsed_time'] = elapsed_time
        
        # 분류 결과를 세션 상태에 저장
        classification_result = {
            "시간": datetime.now(),
            "소음 유형": result.get('prediction', '알 수 없음'),
            "소음 강도(dB)": result.get('spl_peak', 0),
            "평균 강도(dB)": result.get('spl_rms', 0),
            "추정 거리": result.get('estimated_distance', 'N/A'),
            "방향": result.get('direction', '알 수 없음'),
            "분석 시간": elapsed_time
        }
        if "classification_results" not in st.session_state:
            st.session_state["classification_results"] = []
        st.session_state["classification_results"].append(classification_result)
        
        return result, elapsed_time, None  # audio_path는 아직 사용 안 함
    return None, None, None

# 커스텀 스타일
st.markdown("""
    <style>
    div.stButton > button {
        background-color: #2c3e50;
        color: white;
        border-radius: 10px;
        padding: 10px 20px;
        font-size: 16px;
        font-weight: bold;
        border: none;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.2);
    }
    div.stButton > button:hover {
        background-color: #ffcc00;
        color: black;
    }
    </style>
""", unsafe_allow_html=True)

# 알람 설정 관련 함수
def get_alarm_settings(user_id, noise_type):
    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor()
    query = """
        SELECT alarm_distance, alarm_db, sensitivity_level
        FROM alarm_settings
        WHERE user_id = %s AND noise_type = %s
    """
    cursor.execute(query, (user_id, noise_type))
    result = cursor.fetchone()
    conn.close()
    return result

def save_alarm_settings(user_id, noise_type, alarm_distance, alarm_db, sensitivity_level):
    conn = mysql.connector.connect(**config.DB_CONFIG)
    cursor = conn.cursor()
    cursor.execute("SELECT user_id FROM alarm_settings WHERE user_id = %s AND noise_type = %s", (user_id, noise_type))
    existing_record = cursor.fetchone()

    if existing_record:
        query = """
            UPDATE alarm_settings
            SET alarm_distance = %s, alarm_db = %s, sensitivity_level = %s
            WHERE user_id = %s AND noise_type = %s
        """
        values = (alarm_distance, alarm_db, sensitivity_level, user_id, noise_type)
        cursor.execute(query, values)
    else:
        query = """
            INSERT INTO alarm_settings (user_id, noise_type, alarm_distance, alarm_db, sensitivity_level)
            VALUES (%s, %s, %s, %s, %s)
        """
        values = (user_id, noise_type, alarm_distance, alarm_db, sensitivity_level)
        cursor.execute(query, values)
    conn.commit()
    conn.close()

def check_alarm_trigger(spl_peak, user_id, noise_type):
    alarm_settings = get_alarm_settings(user_id, noise_type)
    if alarm_settings:
        _, alarm_db, _ = alarm_settings
        if spl_peak >= alarm_db:
            if spl_peak >= 70:
                alert_message = f"🚨 위험 수준 소음 감지! 최대 소음 강도는 {spl_peak} dB입니다."
                send_alert(alert_message)
            elif spl_peak >= 50:
                alert_message = f"⚠️ 주의 요함! 소음 강도가 {spl_peak} dB입니다."
                send_alert(alert_message)

def send_alert(message):
    print(message)  # 콘솔 출력, 나중에 추가 기능 가능

# NoiseModel_page 클래스
class NoiseModel_page:
    def noisemodel_page(self):
        # 로그인 체크
        if 'user_info' not in st.session_state or 'id' not in st.session_state['user_info']:
            st.warning("로그인이 필요합니다. 로그인 페이지로 이동해주세요.")
            return

        user_id = st.session_state['user_info']['id']
        user_info = get_user_info(user_id)
        st.write(f"로그인된 사용자: {user_info['name']} (ID: {user_id})")

        # 상태 초기화
        if 'tts_enabled' not in st.session_state:
            st.session_state['tts_enabled'] = True
        if 'sos_email_enabled' not in st.session_state:
            st.session_state['sos_email_enabled'] = True
        if 'start_time' not in st.session_state:
            st.session_state['start_time'] = None
        if 'background_audio' not in st.session_state:
            st.session_state['background_audio'] = None
        if 'danger_alert_time' not in st.session_state:
            st.session_state['danger_alert_time'] = None
        if 'email_sent' not in st.session_state:
            st.session_state['email_sent'] = False
        if 'tts_queue' not in st.session_state:
            st.session_state['tts_queue'] = []

        tab1, tab2, tab3 = st.tabs(['소음 분류기', '소음 측정 기록', '알람 기준 설정'])

        with tab1:  # 소음 분류기
            st.markdown("### 소음 분류기 사용 방법", unsafe_allow_html=True)
            st.write("이곳에서 소음을 녹음하거나 파일을 업로드해 분석할 수 있습니다.")
            st.write("분석 결과로 소음 유형과 강도를 확인할 수 있어요!")
            st.write("""🚗 도로에서 나는 소음을 확인하고 싶나요? \n
                 🔔 경적, 사이렌, 주행음, 기타 소음을 구분해 분석해 줍니다!""")
            with st.expander("📖 소음 분류기 사용 매뉴얼 자세히 보기"):
                st.subheader("1️⃣ 소음 분류기란?")
                st.write("소음 분류기는 소리를 녹음하거나 파일을 업로드해 분석하는 서비스입니다.")
                st.write("🚗 도로 소음 / 🚨 경적·사이렌 / 🏭 기타 소음 등 다양한 소리를 인식하고, 결과를 제공합니다.")
                st.write("📢 분석된 소음이 사용자 설정 기준을 초과하면 경고 메시지와 긴급 알림을 보낼 수 있습니다.")

                st.subheader("2️⃣ 사용 방법 (단계별 가이드)")
                st.write("**🎙 1. 소음 녹음 방식**")
                st.write("""직접 소리를 녹음해 분석하는 방법입니다. 👉 녹음 버튼을 누르고, 원하는 소리를 녹음한 뒤 정지하세요.""")
                st.write("  ①  ***배경 소음 녹음 (5초 이상 권장)***")
                st.write("- 기본적인 주변 소음을 녹음하면 분석 정확도를 높일 수 있습니다.")
                st.write("  ② ***목표 소음 녹음***")
                st.write("- 분석하고 싶은 소리를 녹음하세요. 50cm~1m 거리에서 녹음하는 것이 가장 정확합니다.")
                st.warning("""📌 녹음할 때 유의할 점\n\n        ✔ 녹음 환경: 너무 시끄러운 곳에서는 원하는 소음이 묻힐 수 있어요.\n\n        ✔ 마이크 품질: 이어폰 마이크보다는 스마트폰 내장 마이크를 사용하는 것이 더 좋아요.""")
                
                st.subheader("3️⃣ 분석 결과 확인하기")
                st.code("""
예시)
🔊 예측된 소음 유형: 차량 주행음
📊 최대 소음 강도 (dB): 77.5
📊 평균 소음 강도 (dB): 57.73
📏 추정 거리: 23.1 미터
📡 방향: 중앙
⏱️ 분석 소요 시간: 0.20 초
            """)
                st.write("📌 참고: '방향'은 소리가 어디서 들리는지를 알려줍니다. \n\n- 하지만 한쪽 소리만 들리는 파일(모노 타입)로는 방향을 알 수 없어요. \n\n -  양쪽 소리가 모두 담긴 파일(스테레오 타입)을 사용하면 소리가 왼쪽, 오른쪽, 또는 중앙에서 나는지 예측할 수 있습니다!")

                st.subheader("4️⃣ 경고 및 알림 기능")
                st.write("📫 사용자가 설정한 기준에 따라 경고 메시지를 제공합니다.")
                st.code("""
🚨 위험 수준 소음 감지! 즉시 조치가 필요합니다 🚨
⚠️ 주의 요함! 소음이 높습니다 ⚠️
                        """)
                st.write("📌 TTS (음성 안내 기능) 지원: \n\n - 경고 메시지는 음성으로 자동 안내됩니다. \n\n - '소음 분류기 사용 방법' 아래의 'TTS 알림' 토글로 켜거나 끌 수 있으며, 설정은 다음 분석에도 유지됩니다!")
                st.write("📌 긴급 메시지 기능: \n\n - 위험 수준 소음이 감지되면 '안전 확인' 버튼이 나타납니다. \n\n - 1분 이상 응답이 없으면 등록된 이메일로 긴급 알림이 자동 발송됩니다.")

                st.subheader("💡 자주하는 질문 (FAQ)")
                st.write("**Q1. 분석 결과가 이상해요!**")
                st.write("👉 녹음된 소리가 너무 짧거나 음질이 낮으면 분석이 부정확할 수 있어요. 배경 소음 없이 녹음해 주세요!")
                st.write("**Q2. MP3 파일도 업로드할 수 있나요?**")
                st.write("👉 현재는 WAV 파일만 지원하고 있어요. MP3 파일을 변환한 뒤 업로드해 주세요.")
                st.write("**Q3. 실시간으로 소음을 분석할 수도 있나요?**")
                st.write("👉 현재는 녹음된 소리만 분석 가능하지만, 향후 실시간 분석 기능을 추가할 예정이에요!")
                st.write("**Q4: 소음 분류기가 작동하지 않을 때는 어떻게 하나요?**")
                st.write("👉 인터넷 연결을 확인하고, WAV 파일이 16kHz인지 확인하세요. 문제가 지속되면 관리자에게 문의해주세요.")
                st.write("**Q5: 배경 소음은 꼭 녹음해야 하나요?**")
                st.write("👉 필수는 아니지만, 배경 소음을 제공하면 분석 정확도가 높아집니다.")
                st.write("**Q6: SOS 메일이 오지 않아요. 어떻게 해야 하나요?**")
                st.write("👉 SOS 메일 발송이 켜져 있는지 확인하고, 이메일 설정이 올바른지 점검하세요.")

            col1, col2 = st.columns(2)
            with col1:
                st.session_state['tts_enabled'] = st.toggle(
                    "🔊 TTS 알림", 
                    value=st.session_state['tts_enabled'], 
                    help="경고 메시지 및 분석 결과를 음성으로 들을 수 있는 기능입니다."
                )
            with col2:
                st.session_state['sos_email_enabled'] = st.toggle(
                    "📧 SOS 메시지 발송", 
                    value=st.session_state['sos_email_enabled'], 
                    help="경고 후 1분간 반응이 없으면 SOS 메시지가 발송됩니다."
                )
            st.divider()

            with st.expander("🎙 녹음 방식", expanded=True):
                st.subheader("1️⃣ 배경 소음 녹음")
                background_audio = st.audio_input("🎤 배경 소음 녹음 시작 (5초 이상 권장)", key="background_audio_tab1")
                if background_audio:
                    background_path = os.path.join(audio_save_path, "background_audio.wav")
                    with open(background_path, "wb") as f:
                        f.write(background_audio.getvalue())
                    st.session_state['background_audio'] = background_audio
                    st.success(f"📂 배경 소음 저장: {background_path}")

                st.subheader("2️⃣ 실제 소음 녹음")
                audio_data = st.audio_input("🎤 목표 소음 녹음 시작", key="target_audio_tab1")
                if audio_data:
                    file_path = os.path.join(audio_save_path, "recorded_audio.wav")
                    with open(file_path, "wb") as f:
                        f.write(audio_data.getvalue())
                    st.success(f"📂 오디오 저장: {file_path}")

                    if st.button("🎙 음성 예측하기", key="predict_recording_tab1", use_container_width=True):
                        st.session_state['start_time'] = time.time()
                        st.session_state['danger_alert_time'] = None
                        st.session_state['email_sent'] = False
                        st.session_state['tts_queue'] = []
                        status_placeholder = st.empty()
                        with status_placeholder:
                            st.spinner("🔊 분석 중...")
                        files = {"file": ("recorded_audio.wav", audio_data.getvalue(), "audio/wav")}
                        if st.session_state['background_audio']:
                            files["background"] = ("background_audio.wav", st.session_state['background_audio'].getvalue(), "audio/wav")
                        response = requests.post(FASTAPI_URL, files=files)
                        result, elapsed_time, _ = process_prediction(response, mode="recording", user_id=user_id)
                        status_placeholder.write("✅ 분석 완료!")
                        
                        if result:
                            spl_peak = display_prediction_result(result, elapsed_time)
                            check_alarm_trigger(spl_peak, user_id, result.get('prediction', '알 수 없음'))
                            
                            if spl_peak >= 70:
                                show_alert("위험 수준 소음 감지! 즉시 조치가 필요합니다", "danger")
                                if st.session_state['tts_enabled']:
                                    tts_text = f"예측된 소음 유형은 {result.get('prediction', '알 수 없음')}입니다. 최대 소음 강도는 {spl_peak} 데시벨, 평균 소음 강도는 {result.get('spl_rms', 0)} 데시벨입니다."
                                    st.session_state['tts_queue'].append(tts_text)
                            elif spl_peak >= 50:
                                show_alert("주의 요함: 지속적 노출 위험", "warning")
                                if st.session_state['tts_enabled']:
                                    tts_text = f"예측된 소음 유형은 {result.get('prediction', '알 수 없음')}입니다. 최대 소음 강도는 {spl_peak} 데시벨, 평균 소음 강도는 {result.get('spl_rms', 0)} 데시벨입니다."
                                    st.session_state['tts_queue'].append(tts_text)
                            
                            play_tts_queue()

                            if spl_peak >= 70 and st.session_state['sos_email_enabled']:
                                if not st.session_state['danger_alert_time']:
                                    st.session_state['danger_alert_time'] = time.time()
                                
                                if st.button("✅ 안전 확인", key="safety_check_recording", use_container_width=True):
                                    st.session_state['danger_alert_time'] = None
                                    st.session_state['email_sent'] = False
                                    st.success("✅ 안전 확인됨")
                                else:
                                    st.warning("1분 동안 안전 확인 버튼을 누르지 않으면 SOS 메일이 발송됩니다.")
                                    display_timer(st.session_state['danger_alert_time'], user_id, result)

            with st.expander("📁 파일 업로드 방식", expanded=True):
                uploaded_file = st.file_uploader("📂 음성 파일 업로드", type=["wav"], key="uploader_tab1")
                if uploaded_file:
                    st.audio(uploaded_file, format='audio/wav')
                    upload_path = os.path.join(upload_folder, uploaded_file.name)
                    with open(upload_path, "wb") as f:
                        f.write(uploaded_file.getvalue())
                    st.success(f"📂 파일 저장: {upload_path}")
                    
                    if st.button("🎙 음성 예측하기", key="predict_upload_tab1", use_container_width=True):
                        st.session_state['start_time'] = time.time()
                        st.session_state['danger_alert_time'] = None
                        st.session_state['email_sent'] = False
                        st.session_state['tts_queue'] = []
                        status_placeholder = st.empty()
                        with status_placeholder:
                            st.spinner("🔊 분석 중...")
                        response = requests.post(FASTAPI_URL, files={"file": uploaded_file})
                        result, elapsed_time, _ = process_prediction(response, mode="upload", user_id=user_id)
                        status_placeholder.write("✅ 분석 완료!")
                        
                        if result:
                            spl_peak = display_prediction_result(result, elapsed_time)
                            check_alarm_trigger(spl_peak, user_id, result.get('prediction', '알 수 없음'))
                            
                            if spl_peak >= 70:
                                show_alert("위험 수준 소음 감지! 즉시 조치가 필요합니다", "danger")
                                if st.session_state['tts_enabled']:
                                    tts_text = f"예측된 소음 유형은 {result.get('prediction', '알 수 없음')}입니다. 최대 소음 강도는 {spl_peak} 데시벨, 평균 소음 강도는 {result.get('spl_rms', 0)} 데시벨입니다."
                                    st.session_state['tts_queue'].append(tts_text)
                            elif spl_peak >= 50:
                                show_alert("주의 요함: 지속적 노출 위험", "warning")
                                if st.session_state['tts_enabled']:
                                    tts_text = f"예측된 소음 유형은 {result.get('prediction', '알 수 없음')}입니다. 최대 소음 강도는 {spl_peak} 데시벨, 평균 소음 강도는 {result.get('spl_rms', 0)} 데시벨입니다."
                                    st.session_state['tts_queue'].append(tts_text)
                            
                            play_tts_queue()

                            if spl_peak >= 70 and st.session_state['sos_email_enabled']:
                                if not st.session_state['danger_alert_time']:
                                    st.session_state['danger_alert_time'] = time.time()
                                
                                if st.button("✅ 안전 확인", key="safety_check_upload", use_container_width=True):
                                    st.session_state['danger_alert_time'] = None
                                    st.session_state['email_sent'] = False
                                    st.success("✅ 안전 확인됨")
                                else:
                                    st.warning("1분 동안 안전 확인 버튼을 누르지 않으면 SOS 메일이 발송됩니다.")
                                    display_timer(st.session_state['danger_alert_time'], user_id, result)

        with tab2:  # 소음 측정 기록 및 피드백
            st.subheader("소음 측정 기록")
            st.write("여기에서 최근 소음 분류 기록을 확인하고 피드백을 남길 수 있습니다.")

            if "classification_results" not in st.session_state or not st.session_state["classification_results"]:
                st.write("아직 측정 기록이 없습니다.")
            else:
                for i, result in enumerate(st.session_state["classification_results"]):
                    with st.expander(f"기록 #{i+1} - {result['시간'].strftime('%Y-%m-%d %H:%M:%S')}", expanded=False):
                        st.write(f"**소음 유형**: {result['소음 유형']}")
                        st.write(f"**최대 소음 강도**: {result['소음 강도(dB)']} dB")
                        st.write(f"**평균 소음 강도**: {result['평균 강도(dB)']} dB")
                        st.write(f"**추정 거리**: {result['추정 거리']} 미터")
                        st.write(f"**방향**: {result['방향']}")
                        st.write(f"**분석 시간**: {result['분석 시간']:.2f} 초")

                        feedback_key = f"feedback_{i}_{result['시간']}"
                        feedback = st.selectbox(
                            "이 분류가 정확했나요?",
                            ["네", "아니요", "모르겠어요"],
                            key=feedback_key,
                            help="소음 유형이 실제와 맞는지 알려주세요!"
                        )
                        wrong_noise = None
                        if feedback == "아니요":
                            wrong_noise = st.text_input(
                                "어떤 소음이었나요?",
                                key=f"feedback_text_{i}_{result['시간']}"
                            )
                        if st.button("피드백 제출", key=f"submit_{i}_{result['시간']}"):
                            feedback_data = {
                                "시간": result["시간"],
                                "소음 유형": result["소음 유형"],
                                "소음 강도(dB)": result["소음 강도(dB)"],
                                "피드백": feedback,
                                "수정 소음": wrong_noise if feedback == "아니요" else None
                            }
                            pd.DataFrame([feedback_data]).to_csv("feedback.csv", mode="a", index=False, header=not pd.io.common.file_exists("feedback.csv"))
                            st.success("피드백이 저장되었습니다!")

        with tab3:  # 알람 기준 설정
            st.subheader("알람 기준 설정")
            
            DEFAULT_ALARM_DISTANCE = {
                "차량 경적": 10,
                "이륜차 경적": 10,
                "차량 사이렌": 20,
                "차량 주행음": 5,
                "이륜차 주행음": 5,
                "기타 소음": 10
            }
            DEFAULT_ALARM_DB = {
                "차량 경적": 100,
                "이륜차 경적": 100,
                "차량 사이렌": 110,
                "차량 주행음": 90,
                "이륜차 주행음": 90,
                "기타 소음": 85
            }
            SENSITIVITY_MULTIPLIER = {
                "약(🔵)": {"distance": 0.5, "db": -10},
                "중(🟡)": {"distance": 1.0, "db": 0},
                "강(🔴)": {"distance": 1.5, "db": 10}
            }

            selected_sensitivity = st.radio("📢 감도 선택", ["약(🔵)", "중(🟡)", "강(🔴)"], index=1)
            adjusted_alarm_settings = {
                noise_type: {
                    "거리": int(DEFAULT_ALARM_DISTANCE[noise_type] * SENSITIVITY_MULTIPLIER[selected_sensitivity]["distance"]),
                    "데시벨": DEFAULT_ALARM_DB[noise_type] + SENSITIVITY_MULTIPLIER[selected_sensitivity]["db"]
                }
                for noise_type in DEFAULT_ALARM_DISTANCE
            }

            st.subheader("📌 소음 유형별 알람 기준 조정")
            st.write("감도를 선택하면 거리 & 데시벨 값이 자동 설정됩니다. 필요하면 개별적으로 조정하세요.")
            user_alarm_settings = {}
            for noise_type, values in adjusted_alarm_settings.items():
                col1, col2 = st.columns(2)
                with col1:
                    user_distance = st.slider(f"📏 {noise_type} (m)", 1, 25, values["거리"], key=f"{noise_type}_distance")
                with col2:
                    user_db = st.slider(f"🔊 {noise_type} (dB)", 50, 120, values["데시벨"], key=f"{noise_type}_db")
                user_alarm_settings[noise_type] = {"거리": user_distance, "데시벨": user_db}

            if st.button("📌 설정 저장"):
                for noise_type, settings in user_alarm_settings.items():
                    save_alarm_settings(
                        user_id=user_id,
                        noise_type=noise_type,
                        alarm_distance=settings["거리"],
                        alarm_db=settings["데시벨"],
                        sensitivity_level=selected_sensitivity
                    )
                st.success("✅ 알람 설정이 저장되었습니다.")
                st.write(f"📢 **선택한 감도:** {selected_sensitivity}")
                st.subheader("📌 최종 설정값")
                st.table(pd.DataFrame(user_alarm_settings).T)

if __name__ == '__main__':
    m = NoiseModel_page()
    m.noisemodel_page()