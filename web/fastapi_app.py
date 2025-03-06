import os
import shutil
import librosa
import numpy as np
import tensorflow as tf 
import streamlit as st
import io
from fastapi import FastAPI, File, UploadFile
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi import Request
from tensorflow.keras.models import load_model

app = FastAPI()

# GPU 비활성화 (CPU로만 실행)
tf.config.set_visible_devices([], 'GPU')

# 모델 로드 
# model = tf.keras.models.load_model('../ES/cnn_model_6classfication.h5')  #레이블 6개
model = tf.keras.models.load_model('../ES/resnet_model_mfcc50.h5') #레이블 5개 
        

# 거리 및 방향 분석 함수
SPL_REFERENCE = 20e-6  # SPL 기준 참조 값 (보통 20uPa, 공기 중 소리의 기준)
DB_REFERENCE = {
    '이륜차경적': 85, 
    '이륜차주행음': 75, 
    '차량경적': 85, 
    '차량사이렌': 90, 
    '차량주행음': 80,
}

def analyze_audio(file_path, noise_type):
    try:
        y, sr = librosa.load(file_path, sr=None, mono=False)

        # 모노/스테레오 판별
        is_stereo = len(y.shape) == 2 and y.shape[0] == 2

        # RMS SPL(평균 데시벨) 계산
        if is_stereo:
            left_channel = y[0]
            right_channel = y[1]
            rms_total = np.sqrt(np.mean((left_channel + right_channel) ** 2)) / 2
        else:
            rms_total = np.sqrt(np.mean(y ** 2))

        rms_spl = 20 * np.log10(rms_total / SPL_REFERENCE + 1e-6)  # RMS SPL 변환

        # 소음 유형에 따른 SPL 계산 및 거리 추정
        db_ref = DB_REFERENCE.get(noise_type, 85)
        estimated_distance = 1 * (10 ** ((db_ref - rms_spl) / 20))
        
        # 거리 및 방향 분석
        direction = "중앙" if is_stereo else None  # 스테레오에서만 방향 정보 제공
        distance_alert = "알람 없음" if estimated_distance > 10 else "🚨 위험 소음!"

        return estimated_distance, direction, distance_alert
    except Exception as e:
        return None, None, None

@app.get("/")
def read_root():
    return {"message": "소음 분류 모델 API"}


@app.post("/predict/")
async def predict(file: UploadFile = File(...)):

    file_bytes = await file.read() # 업로드된 파일을 바이트로 읽어오기

    # 디버깅
    print(f"파일 이름: {file.filename}")

    # BytesIO로 바이트 데이터를 파일처럼 읽기
    audio_data = librosa.load(io.BytesIO(file_bytes), sr=22050)[0]
    mfccs = librosa.feature.mfcc(y=audio_data, sr=22050, n_mfcc=50)
    features = np.mean(mfccs, axis=1)

    # 모델 예측
    prediction = model.predict(np.array([features]))  
    predicted_label = np.argmax(prediction)  

    # 소음 종류 라벨
    # noise_labels = ['이륜차경적', '이륜차주행음', '차량경적', '차량사이렌', '차량주행음', '기타소음']
    noise_labels = ['이륜차경적', '이륜차주행음', '차량경적', '차량사이렌', '차량주행음']
    # detected_noise = noise_labels[predicted_label]
    if predicted_label < len(noise_labels):
        detected_noise = noise_labels[predicted_label]
    else:
        detected_noise = "알 수 없는 소음"  # 예외 처리

    # 거리 및 방향 분석
    # 소음 파일을 임시로 저장 후 분석
    temp_file_path = f"/tmp/{file.filename}"
    with open(temp_file_path, "wb") as f:
        f.write(file_bytes)

    estimated_distance, direction, distance_alert  = analyze_audio(temp_file_path, detected_noise)
   

    print(f"예측된 소음 유형: {detected_noise}")  # 터미널에 출력

    # 예측 결과 반환
    response = {
        "prediction": prediction,
        "estimated_distance": estimated_distance,
        "direction": direction,
        "distance_alert": distance_alert
    }
    
    # 응답을 jsonable_encoder를 사용하여 직렬화하여 반환
    return response