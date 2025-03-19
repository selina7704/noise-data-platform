import streamlit as st

class NoiseModel_page:
    def noisemodel_page(self):
        # 탭 생성은 클래스 내부에서 할 수 있지만, 
        # 탭을 만들고 각 탭의 내용을 작성하는 코드가 함수 내부에 있을 때 문제가 발생하는 것으로 보입니다.
        tab1, tab2= st.tabs(['소음 분류기', '알람 기준 설정'])
        
        # 소음 분류기'
        with tab1:
            st.subheader('소음 분류기')
            st.write(' ')


        # 알람 기준 설정
        with tab2:
            st.subheader('알람 기준 설정')
            
            
if __name__ == '__main__':
    m = NoiseModel_page()
    m.noisemodel_page()
