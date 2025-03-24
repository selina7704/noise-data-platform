import streamlit as st
from streamlit_option_menu import option_menu
from login import Login_page
from signup import Signup_page
from home_about import About_page
from home_noisemodel import NoiseModel_page
from home_statistics import Statistics_page
from mypage_edit import Edit_page

# # 페이지 설정
# st.set_page_config(
#     page_title="담았소",  # 앱의 제목
#     page_icon="🔊",  # 앱 아이콘 (이모지나 이미지 파일 사용 가능)
#     layout="wide",  # 페이지 레이아웃을 'wide'로 설정
#     initial_sidebar_state="expanded"  # 사이드바를 확장된 상태로 시작
# )

class Home_page:
    def __init__(self):
        self.Login = Login_page()
        self.Signup = Signup_page()
        self.About = About_page()
        self.NoiseModel = NoiseModel_page()
        self.Statistics = Statistics_page()
        self.Edit = Edit_page()

    def main(self, choose=None):
        if choose == "홈":  # 메인 홈화면
            self.bar()
        elif choose == "로그인":  # 로그인
            self.Login.run()
        elif choose == "회원가입":  # 회원가입
            self.Signup.run()
        elif choose == "마이페이지":  # 마이페이지 선택
            self.Edit.run()  # Mypage_page 실행
        elif choose == "로그아웃":
            self.logout()

    def bar(self):
        col, col1, col2, col3 = st.columns([2, 3, 1.5, 1])
        # 상단 중앙: 로고
        with col1:
            st.image("logo2.png", width=450)

        st.write('#')
        # 사이드바 홈 안의 네비게이션바 설정
        nav = ["About", "소음 분류기", "통계 분석"]
        select = option_menu(None, nav,
                             icons=['house', 'volume-up-fill', 'bar-chart-fill'], #사진 추후 수정 
                             default_index=0,
                             styles={
                                 "container": {"padding": "5!important", "background-color": "#fafafa"},
                                 "icon": {"color": "#eebb44", "font-size": "20px"},
                                 "nav-link": {"font-size": "16px", "text-align": "left", "margin": "0px",
                                              "--hover-color": "#eee"},
                                 "nav-link-selected": {"background-color": "#009874"}
                             }, orientation="horizontal"
                             )
        
        # 로그인 필요 페이지 체크
        if select in [nav[1], nav[2]]:
            if "user_info" not in st.session_state or not st.session_state["user_info"]:
                st.warning("로그인이 필요합니다.")
                return  # 로그인하지 않으면 함수 종료
            
        # 네비게이션바
        if select == nav[0]:
            self.About.about_page()
        if select == nav[1]:
            self.NoiseModel.noisemodel_page()
        if select == nav[2]:
            self.Statistics.statistics_page()    

    def logout(self):
        """로그아웃: 세션 초기화"""
        st.session_state.clear()
        st.sidebar.success("로그아웃되었습니다.")

    def run(self):
        # 로그인 상태에 따라 메뉴 변경
        if 'user_info' in st.session_state and st.session_state['user_info']:
            menu = ["홈", "마이페이지", "로그아웃"]
            icons = ['house', 'person lines fill', 'door-open']
        else:
            menu = ["홈", "로그인", "회원가입", "마이페이지"]
            icons = ['house', 'bi-clipboard-check', 'gear', 'person lines fill']
        
        # 사이드바
        with st.sidebar:
            # 세션 상태에서 사용자 이름 가져오기
            if 'user_info' in st.session_state:
                name = st.session_state.user_info['name']
                # 사용자 이름을 사이드바 상단에 표시
                st.markdown(f"<p style='text-align: center; font-weight: bold;'>😊 안녕하세요, {name}님</p>", unsafe_allow_html=True)
                st.write("---")  # 구분선 추가

            choose = option_menu("", menu,
                                 icons=['house', 'bi-clipboard-check', 'gear', 'person lines fill'],
                                 default_index=0,
                                 styles={
                                        "nav-link-selected": {"background-color": "#009874"}  
                                        }
                                 )
        # 네비게이션바에 선택된 페이지 출력
        self.main(choose)

# 앱 실행
if __name__ == "__main__":
    home = Home_page()
    home.run()
