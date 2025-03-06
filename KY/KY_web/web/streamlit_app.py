import streamlit as st
import requests
import io

# FastAPI 서버 URL (서버가 로컬에서 실행 중이면 localhost 사용)
FASTAPI_URL = "http://localhost:8000/predict/"

def main():
    st.title("소음 분류기 및 분석기")

    # 파일 업로드
    uploaded_file = st.file_uploader("음성 파일을 업로드하세요", type=["wav"])

    if uploaded_file is not None:
        st.audio(uploaded_file, format='audio/wav')  # 업로드한 파일을 웹에서 들을 수 있게 표시

        # 예측 버튼 클릭 시 예측 수행
        if st.button('예측하기'):
            # 파일을 FastAPI 서버로 전송
            response = requests.post(FASTAPI_URL, files={"file": uploaded_file.getvalue()})

            if response.status_code == 200:
                result = response.json()
                prediction = result.get("prediction")
                distance = result.get("estimated_distance")
                direction = result.get("direction")
                alert = result.get("distance_alert")
                
                # 예측된 소음 유형과 분석 결과 출력
                st.write(f"예측된 소음 유형: {prediction}")
                st.write(f"추정 거리: {distance} 미터")
                st.write(f"추정 방향: {direction if direction else '알 수 없음'}")
                st.write(f"알람: {alert}")
            else:
                st.write("예측 실패. 다시 시도해 주세요.")

if __name__ == "__main__":
    main()

