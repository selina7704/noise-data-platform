import streamlit as st

class signup_page():
    def __init__(self):
        pass

    def run(self):
        st.header("📝 회원가입")
        
        # 회원가입 폼 구현
        with st.form(key='signup_form'):
            username = st.text_input('아이디')
            password = st.text_input('비밀번호', type='password')
            confirm_password = st.text_input('비밀번호 확인', type='password')
            name = st.text_input('이름')
            age_options = ["~20", "21-30", "31-40", "41-50", "51-60", "61+"]
            age = st.selectbox('나이', age_options)
            email = st.text_input('이메일')
            guardian_email = st.text_input('보호자 이메일')
            phone_number = st.text_input('전화번호')

            usage_purpose = st.selectbox('사용 목적', ['노이즈캔슬링 보조 장치', '청각 보조 장치', '기타'])

            signup_button = st.form_submit_button('가입하기')

        if signup_button:
            if password == confirm_password:
                st.success('회원가입 성공!')
                # 여기에 실제 회원가입 로직을 구현합니다
            else:
                st.error('비밀번호가 일치하지 않습니다.')

        if st.button('로그인 페이지로 돌아가기'):
            st.session_state.page = 'login'
            st.rerun()
