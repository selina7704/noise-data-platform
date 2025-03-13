import streamlit as st
import requests
import numpy as np
import librosa
import io
import os 
import time 
import json
import pandas as pd 
import tensorflow as tf 
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.metrics import classification_report, confusion_matrix

# FastAPI 서버 주소
FASTAPI_URL = "http://localhost:8000/predict/"


# 저장할 디렉토리 생성
upload_folder = "uploads"          # 업로드한 파일 저장 폴더
audio_save_path = "recorded_audio" # 녹음된 파일 저장 폴더
os.makedirs(upload_folder, exist_ok=True)
os.makedirs(audio_save_path, exist_ok=True)
    
def main():
    
    st.title("소음 분류기")

    # 파일 업로드
    uploaded_file = st.file_uploader("음성 파일을 업로드하세요", type=["wav"])

    if uploaded_file is not None:
        st.audio(uploaded_file, format='audio/wav')  
        st.write(f"파일 이름: {uploaded_file.name}")
        
        # 저장할 파일 경로 설정 (uploads 폴더)
        upload_path = os.path.join(upload_folder, uploaded_file.name)

        # 파일 저장
        with open(upload_path, "wb") as f:
            f.write(uploaded_file.getvalue())

        st.success(f"📂 업로드된 파일이 저장되었습니다: {upload_path}")

        if st.button('예측하기'):
            
            start_time = time.time()
            
            # 파일을 FastAPI 서버로 전송
            files = {"file": (uploaded_file.name, uploaded_file.getvalue(), "audio/wav")}
            response = requests.post(FASTAPI_URL, files=files)

            elapsed_time = time.time() - start_time
            
            if response.status_code == 200:
                prediction = response.json()
                if "error" in prediction:
                    st.error("오디오 분석 중 오류 발생! 🚨")
                else:
                    st.success("분석 완료 ✅")
                    st.write(f"**예측된 소음 유형:** {prediction.get('prediction', '알 수 없음')}")
                    st.write(f"**소음 크기 (dB):** {prediction.get('spl', 'N/A')} dB")
                    st.write(f"**추정 거리:** {prediction.get('estimated_distance', 'N/A')} 미터")
                    st.write(f"**방향:** {prediction.get('direction', '알 수 없음')}")
                    st.write(f"⏱️ 예측 소요 시간: {elapsed_time:.2f}초")
            else:
                st.error("서버와의 통신 오류 발생! ❌")
                
    # 사용자 오디오 입력 받기
    audio_value = st.audio_input("음성을 녹음하세요!")

    if audio_value:
        st.audio(audio_value, format='audio/wav')  # 녹음된 오디오 재생
        
        # 저장할 파일 경로 설정
        file_path = os.path.join(audio_save_path, "recorded_audio.wav")
        
        # 파일 저장
        with open(file_path, "wb") as f:
            f.write(audio_value.getvalue())
        
        st.success(f"녹음된 오디오가 저장되었습니다: {file_path}")
        
        start_time = time.time()

        # 녹음된 오디오 파일을 FastAPI 서버로 전송하여 예측 수행
        files = {"file": ("recorded_audio.wav", audio_value.getvalue(), "audio/wav")}
        response = requests.post(FASTAPI_URL, files=files)
        
        elapsed_time = time.time() - start_time

        if response.status_code == 200:
            prediction = response.json()
            if "error" in prediction:
                st.error("오디오 분석 중 오류 발생! 🚨")
            else:
                st.success("분석 완료 ✅")
                st.write(f"**예측된 소음 유형:** {prediction.get('prediction', '알 수 없음')}")
                st.write(f"**소음 크기 (dB):** {prediction.get('spl', 'N/A')} dB")
                st.write(f"**추정 거리:** {prediction.get('estimated_distance', 'N/A')} 미터")
                st.write(f"**방향:** {prediction.get('direction', '알 수 없음')}")
                st.write(f"⏱️ 예측 소요 시간: {elapsed_time:.2f}초")
        else:
            st.error("서버와의 통신 오류 발생! ❌")
    st.title("소음 분류 성능 평가")

    # 파일 업로드
    # uploaded_file = st.file_uploader("CSV 파일을 업로드하세요", type=["csv"])

    # if uploaded_file is not None:
    #     st.write("파일을 성공적으로 업로드했습니다.")
        
    #     # FastAPI 서버로 파일 전송
    #     files = {"file": uploaded_file.getvalue()}
    #     response = requests.post(FASTAPI_URL, files=files)
        
    #     if response.status_code == 200:
    #         result = response.json()
            
    #         # Classification Report 출력
    #         st.subheader("Classification Report:")
    #         st.json(result["classification_report"])
            
    #         # Confusion Matrix 시각화
    #         st.subheader("Confusion Matrix:")
    #         cm = result["confusion_matrix"]
    #         if cm:
    #             plt.figure(figsize=(10, 7))
    #             sns.heatmap(cm, annot=True, fmt='d', cmap='Blues')
    #             plt.title('Confusion Matrix')
    #             plt.xlabel('Predicted Labels')
    #             plt.ylabel('True Labels')
    #             st.pyplot(plt)
            
    #         # 예측 결과 출력
    #         st.subheader("Predictions:")
    #         st.write(result["predictions"])
    #     else:
    #         st.error("FastAPI 서버에서 응답을 받지 못했습니다.")
        

    # Streamlit 앱 제목
    
    
    label_dict = {
        '이륜차경적': 0, '이륜차주행음': 1, '차량경적': 2, '차량사이렌': 3, '차량주행음': 4, '기타소음': 5
    }
    reverse_label_dict = {v: k for k, v in label_dict.items()}
    
    
    # model = tf.keras.models.load_model('../web/resnet_model_modified_v6.h5') 
    tf.config.set_visible_devices([], 'GPU')   
    
    @st.cache_resource
    def load_model():
        model = tf.keras.models.load_model('../web/resnet_model_modified_v6.h5')
        return model 
    
    # # 모델 예측 함수 (예제)
    # def predict_label(df):
    #     mfcc_columns = [f"mfcc_{i}" for i in range(1, 51)]  # 'mfcc_1'부터 'mfcc_50'까지의 열 이름
    #     X_test = df[mfcc_columns].values
        
    #     X_test = X_test.reshape((X_test.shape[0], X_test.shape[1], 1))
    #     print("X_test shape:", X_test.shape)
        
    #     predictions = model.predict(X_test)
    #     predicted_labels = np.argmax(predictions, axis=1)  
    #     predicted_label_names = [reverse_label_dict[label] for label in predicted_labels]   
        
        # # 결과를 DataFrame으로 반환
        # df['predicted_label'] = predicted_label_names
        # result_csv = df.to_csv(index=False)
        
        # df_category_03 = df[['category_03']]
        # print(df_category_03)

        # return {
        #     "Prediction": predicted_label_names,
        #     "Real": df_category_03.to_dict(orient="records")
        # }

    
    def predict_label(df):
        mfcc_columns = [f"mfcc_{i}" for i in range(1, 51)]
        X_test = df[mfcc_columns].values.reshape((df.shape[0], 50, 1))
    
        predictions = model.predict(X_test)
        predicted_labels = np.argmax(predictions, axis=1)
        df['predicted_label'] = [reverse_label_dict[label] for label in predicted_labels]
        return df

    st.title("CSV 파일 업로드 및 미리보기")
    model = load_model()

    
    # CSV 파일 업로드
    uploaded_file = st.file_uploader("CSV 파일을 업로드하세요", type=["csv"])

    if uploaded_file is not None:
        try:
            df = pd.read_csv(uploaded_file)
            st.write("📌 **업로드된 데이터 미리보기**:")
            st.dataframe(df.head())

            # 예측 버튼
            if st.button("예측 실행"):
                df_result = predict_label(df)
                df_result = pd.DataFrame(df_result)
                st.write("🎯 **예측 결과**:")
                # st.dataframe(df_result)
                st.write(df_result.head()) 
                
                            
                # Confusion Matrix 계산
                cm = confusion_matrix(df['category_03'], df['predicted_label'], labels=list(label_dict.keys()))
                report = classification_report(df['category_03'], df['predicted_label'], output_dict=True)
                
                # 분류 보고서 출력
                st.subheader("Classification Report")
                st.json(report)
                
                # Confusion Matrix 시각화
                st.subheader("Confusion Matrix")
                plt.figure(figsize=(8, 6))
                sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', xticklabels=label_dict.keys(), yticklabels=label_dict.keys())
                plt.xlabel("Predicted")
                plt.ylabel("Actual")
                plt.title("Confusion Matrix")
                st.pyplot(plt)
                
                # 예측 결과 다운로드 링크 제공
                csv = df_result.to_csv(index=False).encode('utf-8')
                st.download_button("📥 예측 결과 다운로드", csv, "predictions.csv", "text/csv")
    
        
        except Exception as e:
            st.error(f"🚨 CSV 읽기 오류: {e}")

    else:
        st.info("📂 CSV 파일을 업로드하면 데이터가 표시됩니다.")
            
            
if __name__ == "__main__":
    main()


    
#     # 필요한 MFCC 열을 모델 입력으로 사용
#     mfcc_columns = [f"mfcc_{i}" for i in range(1, 51)]  # 'mfcc_1'부터 'mfcc_50'까지의 열 이름
#     features = df[mfcc_columns].values
    
#     print(f'mfcc_columns: {mfcc_columns}')

#     # 모델 예측
#     predictions = model.predict(features)
#     predicted_labels = np.argmax(predictions, axis=1)

#     # 예측된 라벨을 대응하는 이름으로 변환
#     predicted_label_names = [reverse_label_dict[label] for label in predicted_labels]

#     # 결과를 DataFrame으로 반환
#     df['predicted_label'] = predicted_label_names
#     result_csv = df.to_csv(index=False)

#     return {
#         "predictions": predicted_label_names,
#         "csv_result": result_csv
#     }
