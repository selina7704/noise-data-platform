import streamlit as st

class About_page:
    def about_page(self):
        # 탭 생성은 클래스 내부에서 할 수 있지만, 
        # 탭을 만들고 각 탭의 내용을 작성하는 코드가 함수 내부에 있을 때 문제가 발생하는 것으로 보입니다.
        tab1, tab2, tab3 = st.tabs(['About', '모델 훈련 데이터셋 통계', '개발진 소개'])
        
        # 각 탭에 대한 내용 추가
        with tab1:
            st.subheader('About:house:')
            st.write(' ')
            st.markdown("""
                    ### 여기다가 작성하시면 됩니다 !!
                    ## 안녕
                    ##### 냥이의 하루, 안냥

                    고양이들의 하루가 어제보다 더 건강하고 즐거울 수 있도록  
                    사진으로 간편하게 반려묘의 안구질환을 진단하고 반려묘의 하루를 매일 기록할 수 있는 서비스 입니다.

                    #
                    ###### [주요 서비스]
                    * 📸 안구진단 : 안구사진을 업로드하면 의심스러운 질병을 진단해보세요.              
                    * 📝 하루기록 : 반려묘의 하루를 기록하고 통계를 통해서 반려묘의 건강을 체크해보세요.
                    * 🏥 동물병원 : 지역 선택을 통해 병원의 위치와 간단한 정보를 확인해보세요.
                    * 💬 챗봇 : 고양이에 대해 궁금한 점을 챗봇과 이야기 해보세요.
                    #
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
