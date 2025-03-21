import streamlit as st
import mysql.connector
from config import DB_CONFIG
import uuid

class Edit_page:
    def __init__(self):
        self.db_connection = None
        self.cursor = None

    def connect_db(self):
        """데이터베이스 연결"""
        try:
            self.db_connection = mysql.connector.connect(**DB_CONFIG)
            self.cursor = self.db_connection.cursor(dictionary=True)
            st.success("데이터베이스에 성공적으로 연결되었습니다.")
        except mysql.connector.Error as e:
            st.error(f"DB 연결 오류: {e}")
            self.db_connection = None

    def update_user_info(self, user_info):
        """사용자 정보를 데이터베이스에 업데이트"""
        if not self.db_connection:
            st.error("데이터베이스 연결이 필요합니다.")
            return False

        try:
            query = """
                UPDATE users 
                SET password = %s, name = %s, age = %s, guardian_email = %s, phone_number = %s, usage_purpose = %s
                WHERE username = %s
            """
            values = (
                user_info["password"],
                user_info["name"],
                user_info["age"],
                user_info["guardian_email"],
                user_info["phone_number"],
                user_info["usage_purpose"],
                user_info["username"]
            )
            self.cursor.execute(query, values)
            self.db_connection.commit()
            st.success(f"SQL 쿼리 실행 성공: {self.cursor.rowcount} 행이 업데이트되었습니다.")
            return True
        except mysql.connector.Error as e:
            st.error(f"DB 업데이트 오류: {e}")
            return False


    def run(self):
        # 로그인 여부 체크
        if "user_info" not in st.session_state or not st.session_state["user_info"]:
            st.warning("로그인이 필요합니다.")
            return  # 로그인되지 않으면 함수 종료
        
        st.header("📝 회원 정보 수정")

        # ✅ 세션에서 `user_info` 가져오기 (없으면 빈 dict 반환)
        user_info = st.session_state.get("user_info", {})

        with st.form(key="edit_form"):
            username = st.text_input("아이디 (변경 불가)", value=user_info.get("username", ""), disabled=True)
            st.text_input("이메일 (변경 불가)", value=user_info.get("email", ""), disabled=True)

            password = st.text_input("비밀번호", type="password", value=user_info.get("password", ""))
            password_confirm = st.text_input("비밀번호 확인", type="password", value=user_info.get("password", ""))
            name = st.text_input("이름", value=user_info.get("name", ""))

            age_options = ["0-20", "21-30", "31-40", "41-50", "51-60", "61-70", "71+"]
            age = st.selectbox("나이", age_options, index=age_options.index(user_info.get("age", "21-30")))

            guardian_email = st.text_input("보호자 이메일", value=user_info.get("guardian_email", ""))
            phone_number = st.text_input("전화번호", value=user_info.get("phone_number", ""))

            usage_purpose_options = ["노이즈캔슬링 보조 장치", "청각 보조 장치", "기타"]
            usage_purpose = st.selectbox("사용 목적", usage_purpose_options, 
                                         index=usage_purpose_options.index(user_info.get("usage_purpose", "기타")))

            submit_button = st.form_submit_button("수정")

        if submit_button:
            if password == password_confirm:
                updated_user_info = {
                    "username": username,
                    "password": password,
                    "name": name,
                    "age": age,
                    "guardian_email": guardian_email,
                    "phone_number": phone_number,
                    "usage_purpose": usage_purpose
                }
                self.connect_db()
                if self.update_user_info(updated_user_info):
                    st.session_state["user_info"] = updated_user_info
                    st.success("회원 정보가 성공적으로 수정되었습니다! 😊")
                    with st.expander("수정된 정보 보기"):
                        for key, value in updated_user_info.items():
                            st.write(f"**{key}**: {value}")
                else:
                    st.error("회원 정보 수정 중 오류가 발생했습니다.")
            else:
                st.error("비밀번호와 비밀번호 확인이 일치하지 않습니다.")
        # 디버깅을 위한 세션 상태 출력
        st.write("Current session state:", st.session_state)