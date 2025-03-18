import streamlit as st
from streamlit_option_menu import option_menu
from Mypage import Mypage_page
from Dashboard import Dashboard_page

class Home_page:
    def __init__(self):
        self.Mypage = Mypage_page()  # Mypage_page 초기화
        self.Dashboard = Dashboard_page()  # Dashboard_page 초기화

    def main(self,choose=None):
        menu = ["마이페이지", "대시보드"]

        # 메뉴 선택에 따라 페이지 전환
        if choose == menu[0]:  # 마이페이지 선택
            self.Mypage.run()  # Mypage_page 실행
            st.write('마이페이지 선택')
        elif choose == menu[1]:  # 데시보드 선택
            self.Dashboard.run()  # Dashboard_page 실행
            st.write('대시보드 선택')
        
    def run(self):
        menu = ["마이페이지", "대시보드"]

        # 사이드바
        with st.sidebar:
            choose = option_menu("", menu,
                                 icons=['house', 'bi-clipboard-check', 'gear','person lines fill' ],
                                  default_index=0
                                 )
        # 네비게이션바에 선택된 페이지 출력
        self.main(choose)


# 앱 실행
if __name__ == "__main__":
    home = Home_page()
    home.run()
