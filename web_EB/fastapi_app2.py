# import os
# import shutil
# import librosa
# import numpy as np
# import tensorflow as tf 
# import streamlit as st
# import io
# from fastapi import FastAPI, File, UploadFile
# from fastapi.responses import HTMLResponse
# from fastapi.templating import Jinja2Templates
# from fastapi import Request
# from tensorflow.keras.models import load_model
# import logging 


# app = FastAPI()

# # GPU 비활성화 (CPU로만 실행)
# tf.config.set_visible_devices([], 'GPU')

# # resnet 모델 로드 
# model = tf.keras.models.load_model('../web/resnet_model_modified_v6.h5')       

# # 🔹 소음 유형별 데시벨 기준 설정
# SPL_REFERENCE = 20e-6  # 0dB 기준 음압
# DB_REFERENCE = {
#     "차량 경적": 100,
#     "이륜차 경적": 100,
#     "사이렌": 100,
#     "차량 주행음": 90,
#     "이륜차 주행음": 90,
#     "기타 소음": 85,
# }


# # 🔹 오디오 분석 함수
# def analyze_audio(file_bytes, predicted_label):
#     try:
#         y, sr = librosa.load(io.BytesIO(file_bytes), sr=None, mono=False)
        
#         if y is None or len(y) == 0:
#             logging.error("❌ librosa가 오디오 데이터를 로드하지 못함!")
#             return {"error": "librosa가 오디오 데이터를 로드하지 못함"}
        
#         is_stereo = len(y.shape) == 2 and y.shape[0] == 2

#         if is_stereo:
#             left_channel = y[0]
#             right_channel = y[1]
#             rms_total = np.sqrt(np.mean((left_channel + right_channel) ** 2)) / 2
#         else:
#             rms_total = np.sqrt(np.mean(y ** 2))

#         if rms_total == 0:
#             logging.error("❌ RMS 계산 중 값이 0이 됨!")
#             return {"error": "RMS 계산 오류"}

#         rms_spl = 20 * np.log10(rms_total / SPL_REFERENCE + 1e-6)
#         peak_amplitude = np.max(np.abs(y))
#         peak_spl = 20 * np.log10(peak_amplitude / SPL_REFERENCE + 1e-6)

#         spl_used = peak_spl if predicted_label in ["차량 경적", "이륜차 경적", "사이렌"] else rms_spl
#         db_ref = DB_REFERENCE.get(predicted_label, 85)
#         estimated_distance = round(1 * (10 ** ((db_ref - spl_used) / 20)), 2)
#         estimated_distance = max(0.1, min(estimated_distance, 1000))

#         direction = "알 수 없음"
#         if is_stereo:
#             rms_left = np.sqrt(np.mean(left_channel ** 2))
#             rms_right = np.sqrt(np.mean(right_channel ** 2))
#             spl_left = 20 * np.log10(rms_left / SPL_REFERENCE + 1e-6)
#             spl_right = 20 * np.log10(rms_right / SPL_REFERENCE + 1e-6)
#             db_difference = spl_left - spl_right
#             if abs(db_difference) < 1.5:
#                 direction = "중앙"
#             elif 1.5 <= abs(db_difference) < 3:
#                 direction = "약간 왼쪽" if db_difference > 0 else "약간 오른쪽"
#             else:
#                 direction = "왼쪽" if db_difference > 0 else "오른쪽"
        
#         return {
#             "prediction": predicted_label,
#             "spl": round(spl_used, 2),
#             "estimated_distance": estimated_distance,
#             "direction": direction,
#         }
#     except Exception as e:
#         logging.error(f"❌ 예외 발생: {str(e)}")
#         return {"error": str(e)}



# @app.post("/predict/")
# async def predict(file: UploadFile = File(...)):

#     file_bytes = await file.read() # 업로드된 파일을 바이트로 읽어오기
#     # 디버깅
#     print(f"파일 이름: {file.filename}")

#     # BytesIO로 바이트 데이터를 파일처럼 읽기

#     audio_bytes = io.BytesIO(file_bytes)
    
#     # librosa를 사용해 WAV 파일을 리샘플링
#     audio_librosa, sr_librosa = librosa.load(audio_bytes, sr=None)
#     print("librosa로 처리한 샘플링 레이트:", sr_librosa)
    
#     mfccs = librosa.feature.mfcc(y=audio_librosa, sr=sr_librosa, n_mfcc=50) 
#     features = np.mean(mfccs, axis=1).astype(float)            
#     print(features)
    
#     # 모델 예측
#     prediction = model.predict(np.array([features]))  
#     predicted_label = np.argmax(prediction)  

#     # 소음 종류 라벨
#     noise_labels = ['이륜차경적', '이륜차주행음', '차량경적', '차량사이렌', '차량주행음', '기타소음']
#     detected_noise = noise_labels[predicted_label] 

#     print(f"예측된 소음 유형: {detected_noise}")  # 터미널에 출력
#     result = analyze_audio(file_bytes,detected_noise)
#     print(result)
#     return result 
#     #return {"prediction": detected_noise}

import os
import shutil
import librosa
import numpy as np
import tensorflow as tf 
import streamlit as st
import io
import matplotlib.pyplot as plt
from fastapi import FastAPI, File, UploadFile
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi import Request
from tensorflow.keras.models import load_model
import logging
from fastapi.responses import JSONResponse

app = FastAPI()

# GPU 비활성화 (CPU로만 실행)
tf.config.set_visible_devices([], 'GPU')

# resnet 모델 로드 
model = tf.keras.models.load_model('../web/resnet_model_modified_v6.h5')

# 소음 유형별 데시벨 기준 설정
SPL_REFERENCE = 20e-6
DB_REFERENCE = {
    "차량 경적": 100,
    "이륜차 경적": 100,
    "사이렌": 100,
    "차량 주행음": 90,
    "이륜차 주행음": 90,
    "기타 소음": 85,
}

def analyze_audio(file_bytes, predicted_label):
    try:
        y, sr = librosa.load(io.BytesIO(file_bytes), sr=None, mono=False)
        if y is None or len(y) == 0:
            logging.error("librosa가 오디오 데이터를 로드하지 못함!")
            return {"error": "librosa가 오디오 데이터를 로드하지 못함"}

        is_stereo = len(y.shape) == 2 and y.shape[0] == 2
        if is_stereo:
            left_channel, right_channel = y[0], y[1]
            rms_total = np.sqrt(np.mean((left_channel + right_channel) ** 2)) / 2
        else:
            rms_total = np.sqrt(np.mean(y ** 2))

        rms_spl = 20 * np.log10(rms_total / SPL_REFERENCE + 1e-6)
        peak_amplitude = np.max(np.abs(y))
        peak_spl = 20 * np.log10(peak_amplitude / SPL_REFERENCE + 1e-6)
        
        spl_used = peak_spl if predicted_label in ["차량 경적", "이륜차 경적", "사이렌"] else rms_spl
        db_ref = DB_REFERENCE.get(predicted_label, 85)
        estimated_distance = round(1 * (10 ** ((db_ref - spl_used) / 20)), 2)
        estimated_distance = max(0.1, min(estimated_distance, 1000))
        
        return {
            "prediction": predicted_label,
            "spl": round(spl_used, 2),
            "estimated_distance": estimated_distance,
        }
    except Exception as e:
        logging.error(f"예외 발생: {str(e)}")
        return {"error": str(e)}

@app.post("/predict/")
async def predict(file: UploadFile = File(...)):
    file_bytes = await file.read()
    audio_bytes = io.BytesIO(file_bytes)
    audio_librosa, sr_librosa = librosa.load(audio_bytes, sr=None)
    mfccs = librosa.feature.mfcc(y=audio_librosa, sr=sr_librosa, n_mfcc=50)
    features = np.mean(mfccs, axis=1).astype(float)
    prediction = model.predict(np.array([features]))
    predicted_label = np.argmax(prediction)
    noise_labels = ['이륜차경적', '이륜차주행음', '차량경적', '차량사이렌', '차량주행음', '기타소음']
    detected_noise = noise_labels[predicted_label]
    result = analyze_audio(file_bytes, detected_noise)

    # 🔹 시각화 (알람 기능)
    fig, ax = plt.subplots()
    categories = list(DB_REFERENCE.keys())
    values = [DB_REFERENCE[cat] for cat in categories]
    ax.bar(categories, values, color='gray', alpha=0.5, label='기준 데시벨')
    ax.bar([detected_noise], [result['spl']], color='red', alpha=0.7, label='현재 소음')
    ax.set_ylabel("데시벨(dB)")
    ax.set_title("소음 강도 시각화")
    ax.legend()
    
    img_path = "static/noise_chart.png"
    plt.savefig(img_path)
    plt.close()

    return JSONResponse({"result": result, "image_url": img_path})