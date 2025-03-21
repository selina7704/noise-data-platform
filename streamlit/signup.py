import streamlit as st
import mysql.connector
from mysql.connector import Error
from config import DB_CONFIG

class Signup_page():
    def __init__(self):
        self.db_connection = None
    
    def connect_db(self):
        try:
            self.db_connection = mysql.connector.connect(
                host=DB_CONFIG['host'],        # MySQL 서버 주소
                user=DB_CONFIG['user'],        # MySQL 사용자명
                password=DB_CONFIG['password'],# MySQL 비밀번호
                database=DB_CONFIG['database'],# 데이터베이스 이름
                port=DB_CONFIG['port'], # MySQL 포트
                #charset='utf8mb4' 
            )
            if self.db_connection.is_connected():
                st.success("MySQL 데이터베이스에 연결되었습니다.")
                # st.write("MySQL 데이터베이스에 연결되었습니다.")  
                # st.write(f"DB 연결 상태: {self.db_connection.is_connected()}")
        except Error as e:
            st.error(f"DB 연결 오류: {e}")
            self.db_connection = None
        
    def save_to_db(self, user_info):
        if self.db_connection:
            cursor = self.db_connection.cursor()
            query = """INSERT INTO users (username, password, name, age, email, guardian_email, phone_number, usage_purpose)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"""
            try:
                cursor.execute(query, (user_info['username'], user_info['password'], user_info['name'], user_info['age'],
                                       user_info['email'], user_info['guardian_email'], user_info['phone_number'], user_info['usage_purpose']))
                self.db_connection.commit()
                st.success("회원가입 정보가 저장되었습니다.")
            except Error as e:
                st.error(f"DB에 저장하는 중 오류 발생: {e}")
            finally:
                cursor.close() 

    def run(self):        
        st.header("📝 회원가입")
        
        # 회원가입 폼 구현
        with st.form(key='signup_form'):
            username = st.text_input('아이디')
            password = st.text_input('비밀번호', type='password')
            confirm_password = st.text_input('비밀번호 확인', type='password')
            name = st.text_input('이름')
            age_options = ["0-20", "21-30", "31-40", "41-50", "51-60", "61-70", "71+"]
            age = st.selectbox('나이', age_options)
            email = st.text_input('이메일')
            guardian_email = st.text_input('보호자 이메일')
            phone_number = st.text_input('전화번호')
            usage_purpose = st.selectbox('사용 목적', ['노이즈캔슬링 보조 장치', '청각 보조 장치', '기타'])

            signup_button = st.form_submit_button('가입하기')

        if signup_button:
            # 빈 입력 필드 확인
            missing_fields = []
            if not username:
                missing_fields.append("아이디")
            if not password:
                missing_fields.append("비밀번호")
            if not confirm_password:
                missing_fields.append("비밀번호 확인")
            if not name:
                missing_fields.append("이름")
            if not email:
                missing_fields.append("이메일")
            if not guardian_email:
                missing_fields.append("보호자 이메일")
            if not phone_number:
                missing_fields.append("전화번호")

            if missing_fields:
                st.error(f"{', '.join(missing_fields)} 입력해야 합니다.")
                return

            # 비밀번호 일치 확인
            if password != confirm_password:
                st.error('비밀번호가 일치하지 않습니다.')
                return

            # 세션 상태에 사용자 정보 저장
            st.session_state.user_info = {
                'username': username,
                'password': password,
                'name': name,
                'age': age,
                'email': email,
                'guardian_email': guardian_email,
                'phone_number': phone_number,
                'usage_purpose': usage_purpose
            }
            st.write(st.session_state.user_info)  
            
            # DB에 저장
            user_info = st.session_state.user_info
            st.write(user_info)
            self.connect_db()  
            self.save_to_db(user_info)  
            
            # 자동 로그인 처리
            st.success(f'{name}님, 회원가입을 축하합니다!')
            st.session_state.logged_in = True
            # st.session_state.page = 'Home'  # 홈 페이지로 이동
            # st.rerun()  # 페이지 새로 고침 (홈 페이지로 이동)