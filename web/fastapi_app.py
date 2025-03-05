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

# UPLOAD_DIR = "uploads"
# os.makedirs(UPLOAD_DIR, exist_ok=True)  # 업로드 폴더 생성

# # GPU 비활성화 (CPU로만 실행)
# tf.config.set_visible_devices([], 'GPU')

# # 모델 로딩 (사전에 학습된 모델 파일 로딩)
# #model = tf.keras.models.load_model('../ES/cnn_model_6classfication.h5')
# model = tf.keras.models.load_model('../ES/resnet_model_mfcc50.h5')


# # HTML 템플릿 경로 설정
# templates = Jinja2Templates(directory="templates")

# # 홈 페이지 렌더링 (파일 업로드 폼)
# @app.get("/", response_class=HTMLResponse)
# async def get_home(request: Request):
#     return templates.TemplateResponse("index.html", {"request": request})

# # 파일 업로드 처리 및 예측
# @app.post("/upload/")
# async def upload_file(file: UploadFile = File(...)):
#     file_location = f"{UPLOAD_DIR}/{file.filename}"
#     with open(file_location, "wb") as buffer:
#         shutil.copyfileobj(file.file, buffer)
    
#     # 업로드된 파일을 처리하여 예측
#     prediction = predict_noise(file_location)
    
#     return {"filename": file.filename, "prediction": prediction}

# 기본 엔드포인트 추가
@app.get("/")
def read_root():
    return {"message": "소음 분류 모델 API"}


# 예측 함수 (음성 파일을 처리 및 소음 예측 결과 반환)
def predict_noise(file_path: str):
    # WAV 파일 로딩
    audio, sr = librosa.load(file_path, sr=None)

    # MFCC 특징 50개 추출
    mfccs = librosa.feature.mfcc(y=audio, sr=sr, n_mfcc=50)
    mfccs = np.mean(mfccs, axis=1)  # 평균값으로 압축

    # 모델 예측 (입력: MFCC 특징, 출력: 소음 종류)
    mfccs = np.reshape(mfccs, (1, 50))  # 모델에 맞게 형태 변경
    prediction = model.predict(mfccs)

    noise_labels = ['이륜차경적', '이륜차주행음', '차량경적', '차량사이렌', '차량주행음']
    predicted_label = noise_labels[np.argmax(prediction)]  # 예측된 라벨
    print(f"예측된 소음 유형: {predicted_label}")  # 터미널에 출력
    return predicted_label

# 예측 엔드포인트
@app.post("/predict/")
async def predict(file: UploadFile = File(...)):
    file_bytes = await file.read()
    result = predict_noise(file_bytes)
    return {"prediction": result}


# from fastapi import FastAPI, Request, File, UploadFile
# from fastapi.responses import JSONResponse
# from fastapi.templating import Jinja2Templates
# import tensorflow as tf
# import numpy as np
# import librosa
# import uvicorn
# import shutil
# import os 

# # GPU 비활성화 (CPU로만 실행)
# tf.config.set_visible_devices([], 'GPU')

# # 모델 로드 (CNN 모델 사용)
# model = tf.keras.models.load_model('../ES/cnn_model_6classfication.h5')

# # FastAPI 앱 생성
# app = FastAPI()

# # Jinja2 템플릿 설정 (HTML 렌더링을 위해)
# templates = Jinja2Templates(directory="templates")

# @app.get("/")
# async def index(request: Request):
#     return templates.TemplateResponse("index.html", {"request": request})

# @app.post("/noise")
# async def noise_detection(request: Request):
#     data = await request.json()
#     volume = data.get('volume', 0)

#     # 오디오 데이터를 받아서 MFCC 변환 후 예측 수행
#     audio_data = np.array([volume])  # 예시로 volume을 사용 (실제 오디오 데이터 처리 필요)
#     features = extract_mfcc(audio_data)  # MFCC 추출

#     # 모델 예측
#     prediction = model.predict(np.array([features]))  
#     predicted_label = np.argmax(prediction)  # 예측된 클래스 인덱스

#     # 소음 종류 라벨
#     noise_labels = ['이륜차경적', '이륜차주행음', '차량경적', '차량사이렌', '차량주행음']
#     detected_noise = noise_labels[predicted_label]

#     print(f"예측된 소음 유형: {detected_noise}")  # 터미널에 출력

#     return JSONResponse(content={"message": f"{detected_noise} 감지!"})

# def extract_mfcc(audio_data, n_mfcc=50):
#     mfccs = librosa.feature.mfcc(y=audio_data, sr=22050, n_mfcc=n_mfcc)
#     return np.mean(mfccs, axis=1)

# if __name__ == "__main__":
#     uvicorn.run(app, host="0.0.0.0", port=5000, reload=True)

