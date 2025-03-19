import streamlit as st

class About_page:
    def about_page(self):
        # 탭 생성은 클래스 내부에서 할 수 있지만, 
        # 탭을 만들고 각 탭의 내용을 작성하는 코드가 함수 내부에 있을 때 문제가 발생하는 것으로 보입니다.
        tab1, tab2, tab3 = st.tabs(['About', '모델 훈련 데이터셋 통계', '개발진 소개'])
        
        # 각 탭에 대한 내용 추가
        with tab1:
            st.subheader('📢 담았소 프로젝트: AI 기반 위험 소음 감지 및 분석 플랫폼')
            st.write(' ')
            st.markdown("""
                ### 🔍 담았소 프로젝트란?
                담았소 프로젝트는 **AI 기반 위험 소음 감지 및 분석 플랫폼**으로,  
                일상적인 도로환경에서 소음 데이터를 수집하고 AI 모델을 이용해 분석하여  
                **교통 소음의 종류를 분류하고, 소음의 방향과 거리를 계산하여, 사용자에게 위험 경고를 제공하는 서비스**입니다.
            """)

            st.subheader("🚀 주요 기능")
            st.markdown("""
            - 📊 **소음 분류:** 차량 경적, 사이렌, 주행음 등 교통 소음을 감지하고 분류 
            - 🎯 **소리 방향 탐지:** 소리의 크기(SPL)와 음파 패턴을 기반으로 방향 판별
            - 📏 **거리 분석:** 소음 강도를 분석하여 소리가 발생한 거리 추정정
            - 🔔 **경고 시스템:** 위험 소음 감지 시 사용자에게 실시간간 알람 제공
            - 🎙 **개인 맞춤형 서비스:** 소리의 크기에 따라 위험 소음 알람 범위를 직접 설정
            - 📡 **소음 데이터 분석 리포트:** 사용자가 경험한 소음을 분석하고 인사이트 제공
            """)

        # 모델 훈련 데이터셋 통계
        with tab2:
            st.subheader('모델 훈련 데이터셋 통계')

        # 개발진 소개
        with tab3:

            # 박은서 소개
            col1, col2 = st.columns([1, 3])

            with col1:
                # GitHub 프로필 사진 추가
                st.image("https://avatars.githubusercontent.com/EunSeo35", width=100)

            with col2:
                st.markdown("""
                <h3 style="color: #000000; font-family: 'Arial', sans-serif;">박은서</h3>
                <a href="https://github.com/EunSeo35" target="_blank">
                    <img src="https://github.githubassets.com/images/modules/logos_page/GitHub-Mark.png" width="25" alt="GitHub Logo" />
                </a>                   
                <p style="font-size: 16px;margin-top: 10px;">데이터 엔지니어, 웹 개발자 </p>
                """, unsafe_allow_html=True)

            st.write("---")

            # 노은비 소개
            col1, col2 = st.columns([1, 3])

            with col1:
                # GitHub 프로필 사진 추가
                st.image("https://avatars.githubusercontent.com/selina7704", width=100)

            with col2:
                st.markdown("""
                <h3 style="color: #000000; font-family: 'Arial', sans-serif;">노은비</h3>
                <a href="https://github.com/selina7704" target="_blank">
                    <img src="https://github.githubassets.com/images/modules/logos_page/GitHub-Mark.png" width="25" alt="GitHub Logo" />
                </a>                   
                <p style="font-size: 16px;margin-top: 10px;">데이터 엔지니어, 웹 개발자 </p>
                """, unsafe_allow_html=True)
            
            st.write("---")
            
            # 엄기영 소개
            col1, col2 = st.columns([1, 3])

            with col1:
                # GitHub 프로필 사진 추가
                st.image("https://avatars.githubusercontent.com/Eomcoco", width=100)

            with col2:
                st.markdown("""
                <h3 style="color: #000000; font-family: 'Arial', sans-serif;">엄기영</h3>
                <a href="https://github.com/Eomcoco" target="_blank">
                    <img src="https://github.githubassets.com/images/modules/logos_page/GitHub-Mark.png" width="25" alt="GitHub Logo" />
                </a>               
                <p style="font-size: 16px;margin-top: 10px;">데이터 분석가, 웹 개발자</p>
                """, unsafe_allow_html=True)
                
                
                
            st.write("---")
            
            #두지원 소개
            col1, col2 = st.columns([1, 3])

            with col1:
                # GitHub 프로필 사진 추가
                st.image("https://avatars.githubusercontent.com/JiwonDu", width=100)

            with col2:
                st.markdown("""
                <h3 style="color: #000000; font-family: 'Arial', sans-serif;">두지원</h3>
                <a href="https://github.com/JiwonDu" target="_blank">
                    <img src="https://github.githubassets.com/images/modules/logos_page/GitHub-Mark.png" width="25" alt="GitHub Logo" />
                </a>               
                <p style="font-size: 16px;margin-top: 10px;">데이터 분석가, 웹 개발자</p>
                """, unsafe_allow_html=True)
            

if __name__ == '__main__':
    m = About_page()
    m.about_page()
