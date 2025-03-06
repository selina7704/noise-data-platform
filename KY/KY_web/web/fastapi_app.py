import os
import librosa
import numpy as np
import joblib
from fastapi import FastAPI, File, UploadFile
from pydantic import BaseModel

# FastAPI 앱 초기화
app = FastAPI()

# 모델 로딩 (저장된 모델 경로 지정)
# 모델 파일을 절대 경로로 지정
model = joblib.load("/home/lab09/git/noise-data-platform/KY/KY_web/web/lgbm_model.joblib")



 # 예시로 LGBM 모델을 로드합니다.

# 🔹 소음 유형별 데시벨 기준 설정
SPL_REFERENCE = 20e-6  # 0dB 기준 음압
DB_REFERENCE = {
    "차량 경적": 100,
    "이륜차 경적": 100,
    "사이렌": 100,
    "차량 주행음": 90,
    "이륜차 주행음": 90,
    "기타 소음": 85,
}

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

    noise_labels = ['이륜차 경적', '이륜차 주행음', '차량 경적', '차량 사이렌', '차량 주행음']
    predicted_label = noise_labels[np.argmax(prediction)]  # 예측된 라벨
    return predicted_label

# 거리 및 방향 분석 함수
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

# 예측 엔드포인트
@app.post("/predict/")
async def predict(file: UploadFile = File(...)):
    file_bytes = await file.read()
    
    # 임시 파일 저장
    file_path = f"temp_{file.filename}"
    with open(file_path, "wb") as f:
        f.write(file_bytes)
    
    # 예측 및 분석 수행
    prediction = predict_noise(file_path)
    estimated_distance, direction, distance_alert = analyze_audio(file_path, prediction)
    
    # 예측 결과 반환
    return {
        "prediction": prediction,
        "estimated_distance": estimated_distance,
        "direction": direction,
        "distance_alert": distance_alert
    }


