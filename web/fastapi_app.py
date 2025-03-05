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
        

@app.get("/")
def read_root():
    return {"message": "소음 분류 모델 API"}


@app.post("/predict/")
async def predict(file: UploadFile = File(...)):

    file_bytes = await file.read() # 업로드된 파일을 바이트로 읽어오기

    # 디버깅
    print(f"파일 이름: {file.filename}")
    print(f"파일 크기: {len(file_bytes)} 바이트")

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


    print(f"예측된 소음 유형: {detected_noise}")  # 터미널에 출력

    return {"prediction": detected_noise}



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

