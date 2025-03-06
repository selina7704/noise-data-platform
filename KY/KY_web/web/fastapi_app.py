from fastapi import FastAPI, File, UploadFile
import os
import librosa
import numpy as np
import joblib
from pydantic import BaseModel

app = FastAPI()

# 모델 로딩 (저장된 모델 경로 지정)
model = joblib.load("/home/lab09/git/noise-data-platform/KY/KY_web/web/lgbm_model.joblib")

SPL_REFERENCE = 20e-6  # 0dB 기준 음압
DB_REFERENCE = {
    "차량 경적": 100,
    "이륜차 경적": 100,
    "사이렌": 100,
    "차량 주행음": 90,
    "이륜차 주행음": 90,
    "기타 소음": 85,
}

def predict_noise(file_path: str):
    audio, sr = librosa.load(file_path, sr=None)
    mfccs = librosa.feature.mfcc(y=audio, sr=sr, n_mfcc=50)
    mfccs = np.mean(mfccs, axis=1)
    mfccs = np.reshape(mfccs, (1, 50))
    prediction = model.predict(mfccs)
    
    noise_labels = ['이륜차 경적', '이륜차 주행음', '차량 경적', '차량 사이렌', '차량 주행음']
    predicted_label = noise_labels[np.argmax(prediction)]
    return predicted_label

def analyze_audio(file_path, noise_type):
    try:
        y, sr = librosa.load(file_path, sr=None, mono=False)
        is_stereo = len(y.shape) == 2 and y.shape[0] == 2

        if is_stereo:
            left_channel = y[0]
            right_channel = y[1]
            rms_total = np.sqrt(np.mean((left_channel + right_channel) ** 2)) / 2
        else:
            rms_total = np.sqrt(np.mean(y ** 2))

        rms_spl = 20 * np.log10(rms_total / SPL_REFERENCE + 1e-6)
        db_ref = DB_REFERENCE.get(noise_type, 85)
        estimated_distance = 1 * (10 ** ((db_ref - rms_spl) / 20))
        direction = "중앙" if is_stereo else None
        distance_alert = "알람 없음" if estimated_distance > 10 else "🚨 위험 소음!"

        return estimated_distance, direction, distance_alert
    except Exception as e:
        return None, None, None

@app.post("/predict/")
async def predict(file: UploadFile = File(...)):
    file_bytes = await file.read()
    file_path = f"temp_{file.filename}"
    
    with open(file_path, "wb") as f:
        f.write(file_bytes)
    
    prediction = predict_noise(file_path)
    estimated_distance, direction, distance_alert = analyze_audio(file_path, prediction)
    
    # 파일 삭제
    os.remove(file_path)
    
    return {
        "prediction": prediction,
        "estimated_distance": estimated_distance,
        "direction": direction,
        "distance_alert": distance_alert
    }

