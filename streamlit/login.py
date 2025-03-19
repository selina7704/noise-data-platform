# import streamlit as st

# #로그인 페이지 
# class login_page:
    
#     def run(self):
#         # 레이아웃 설정
#         col1, col2, col3 = st.columns([2, 1, 2])
#         col2.subheader('로그인 :)')
#         col4, col5, col6 = st.columns([1, 2, 1])
        
#         # 로그인 기능
#         with col5:
#             if self.service.login_user(print1=False,print2=False)=='':
#                 login_id = st.text_input('아이디', placeholder='아이디를 입력하세요')
#                 login_pw = st.text_input('패스워드',placeholder='패스워드를 입력하세요', type='password')
#                 login_btn = st.button('로그인하기')
#                 if login_btn:
#                     self.service.login(login_id, login_pw)
#             else:
#                 self.service.logout()
# if __name__ == '__main__':
#     m = login_page()
#     m.run()

import streamlit as st

class login_page:
    def __init__(self):
        # 초기화는 객체 생성 시 한 번만 호출되고, run에서 페이지 로직을 처리합니다.
        pass
    def run(self):
        st.header("🔊 로그인")
        with st.form(key='login_form'):
            username = st.text_input('아이디')
            password = st.text_input('비밀번호', type='password')
            submit_button = st.form_submit_button('로그인')

        if submit_button:
            # 여기에 로그인 검증 로직을 구현합니다
            if username == 'admin' and password == 'password':
                st.success('로그인 성공!')
            else:
                st.error('로그인 실패. 사용자 이름 또는 비밀번호를 확인해주세요.')
        
        st.markdown("<br>", unsafe_allow_html=True)  # 간격 추가
        if st.button('회원가입하기'):
            # 세션 상태를 사용하여 signup 페이지로 전환
            st.session_state.page = 'signup'
            st.experimental_rerun()

