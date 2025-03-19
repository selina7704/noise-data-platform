import streamlit as st
from streamlit_option_menu import option_menu
from login import login_page
from Mypage import Mypage_page
from Dashboard import Dashboard_page
<<<<<<< HEAD
from signup import signup_page
=======
from home_about import About_page
from home_noisemodel import NoiseModel_page
from home_statistics import Statistics_page
>>>>>>> 26fe8dcc23664dd4eddc2364c73b846c44b6b109

class Home_page:
    def __init__(self):
        self.login = login_page()
        self.Mypage = Mypage_page()  # Mypage_page 초기화
        self.Dashboard = Dashboard_page()  # Dashboard_page 초기화
<<<<<<< HEAD
        self.signup = signup_page()

    def main(self,choose=None):
        menu = ["마이페이지", "대시보드", '로그인','회원가입']
=======
        self.About = About_page()
        self.NoiseModel = NoiseModel_page()
        self.Statistics = Statistics_page()

    def main(self, choose=None):
        menu = ["홈","마이페이지", "대시보드", '로그인']
>>>>>>> 26fe8dcc23664dd4eddc2364c73b846c44b6b109

        # 메뉴 선택에 따라 페이지 전환
        if choose == menu[0]: # 메인 홈화면
            self.bar() 
        elif choose == menu[1]:  # 마이페이지 선택
            self.Mypage.run()  # Mypage_page 실행
            st.write('마이페이지 선택')
        elif choose == menu[2]:  # 대시보드 선택
            self.Dashboard.run()  # Dashboard_page 실행
<<<<<<< HEAD
        elif choose == menu[2]: #login
            self.login.run()
        elif choose == menu[3]: #회원가입
            self.signup.run()   


    def run(self):
        menu = ["마이페이지", "대시보드", '로그인', '회원가입']
=======
        elif choose == menu[3]:  # 로그인 선택
            self.login.run()

    def bar(self):
        col, col1, col2, col3 = st.columns([2, 3, 1.5, 1])
        # 상단 중앙: 로고
        with col1:
            st.markdown('## 담았소')
        # 상단 오른쪽: 반려묘 선택
        # with col3:
        #     self.petsv.printMyCat(print1=False)

        st.write('#')
        # 사이드바 홈 안의 네비게이션바 설정
        nav = ["About", "소음 분류기", "통계 분석"]
        select = option_menu(None, nav,
                             icons=['house', 'camera fill', 'book'], #사진 추후 수정 
                             default_index=0,
                             styles={
                                 "container": {"padding": "5!important", "background-color": "#fafafa"},
                                 "icon": {"color": "orange", "font-size": "25px"},
                                 "nav-link": {"font-size": "16px", "text-align": "left", "margin": "0px",
                                              "--hover-color": "#eee"},
                                 "nav-link-selected": {"background-color": "#02ab21"}
                             }, orientation="horizontal"
                             )
        
        
        # 네비게이션바
        if select == nav[0]:
            self.About.about_page()
        if select == nav[1]:
            self.NoiseModel.noisemodel_page()
        if select == nav[2]:
            self.Statistics.statistics_page()    

    def run(self):
        menu = ["홈","마이페이지", "대시보드", '로그인']
>>>>>>> 26fe8dcc23664dd4eddc2364c73b846c44b6b109

        # 사이드바
        with st.sidebar:
            choose = option_menu("", menu,
                                 icons=['house', 'bi-clipboard-check', 'gear', 'person lines fill'],
                                 default_index=0
                                 )
        # 네비게이션바에 선택된 페이지 출력
        self.main(choose)


# 앱 실행
if __name__ == "__main__":
    home = Home_page()
    home.run()
