import streamlit as st
import uuid

class Edit_page:
    def __init__(self):
        pass

    def run(self):
        # 로그인 여부 체크
        if "user_info" not in st.session_state or not st.session_state["user_info"]:
            st.warning("로그인이 필요합니다.")
            return  # 로그인되지 않으면 함수 종료
        
        st.header("📝 회원 정보 수정")

        # ✅ 세션에서 `user_info` 가져오기 (없으면 빈 dict 반환)
        user_info = st.session_state.get("user_info", {})

        # ✅ `user_info["id"]`가 없을 경우, 랜덤한 UUID 사용하여 충돌 방지
        form_key = f"edit_form_{user_info.get('id', 'unknown')}_{uuid.uuid4().hex}"

        with st.form(key=form_key):
            st.text_input("아이디 (변경 불가)", value=user_info.get("id", ""), disabled=True)
            st.text_input("이메일 (변경 불가)", value=user_info.get("email", ""), disabled=True)

            password = st.text_input("비밀번호", type="password", value=user_info.get("password", ""), key=f"{form_key}_password")
            password_confirm = st.text_input("비밀번호 확인", type="password", value=user_info.get("password", ""), key=f"{form_key}_password_confirm")
            name = st.text_input("이름", value=user_info.get("name", ""), key=f"{form_key}_name")

            age_options = ["0-20", "21-30", "31-40", "41-50", "51-60", "61-70", "71+"]
            age = st.selectbox("나이", age_options, index=age_options.index(user_info.get("age", "21-30")), key=f"{form_key}_age")

            guardian_email = st.text_input("보호자 이메일", value=user_info.get("guardian_email", ""), key=f"{form_key}_guardian_email")
            phone_number = st.text_input("전화번호", value=user_info.get("phone_number", ""), key=f"{form_key}_phone_number")

            usage_purpose_options = ["노이즈캔슬링 보조 장치", "청각 보조 장치", "기타"]
            usage_purpose = st.selectbox("사용 목적", usage_purpose_options, 
                                         index=usage_purpose_options.index(user_info.get("usage_purpose", "기타")), 
                                         key=f"{form_key}_usage_purpose")

            submit_button = st.form_submit_button("수정")

        if submit_button:
            if password == password_confirm:
                st.success("회원 정보가 수정되었습니다!")

                # 🔹 session 정보 업데이트
                st.session_state.user_info.update({
                    "password": password,
                    "name": name,
                    "age": age,
                    "guardian_email": guardian_email,
                    "phone_number": phone_number,
                    "usage_purpose": usage_purpose
                })

                st.rerun()
            else:
                st.error("비밀번호와 비밀번호 확인이 일치하지 않습니다.")
