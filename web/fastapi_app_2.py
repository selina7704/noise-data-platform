import logging
from fastapi import FastAPI, File, UploadFile
import librosa
import numpy as np
import io
import tensorflow as tf

app = FastAPI()
logging.basicConfig(level=logging.DEBUG)  # 디버깅 로그 활성화

# 🔹 ResNet 모델 로드
resnet_model = tf.keras.models.load_model("resnet_model_modified_v6.h5")

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

NOISE_LABELS = ["이륜차 경적", "이륜차 주행음", "차량 경적", "사이렌", "차량 주행음", "기타 소음"]

# 🔹 MFCC 특징 추출 함수
def extract_mfcc(file_bytes, n_mfcc=50):
    y, sr = librosa.load(io.BytesIO(file_bytes), sr=None)
    mfccs = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=n_mfcc)
    features = np.mean(mfccs, axis=1).reshape(1, -1)  # 모델 입력에 맞게 차원 변환
    logging.debug(f"🔍 추출된 MFCC 특징 벡터 크기: {features.shape}")
    return features

# 🔹 오디오 분석 함수
def analyze_audio(file_bytes, predicted_label):
    try:
        y, sr = librosa.load(io.BytesIO(file_bytes), sr=None, mono=False)
        
        if y is None or len(y) == 0:
            logging.error("❌ librosa가 오디오 데이터를 로드하지 못함!")
            return {"error": "librosa가 오디오 데이터를 로드하지 못함"}
        
        is_stereo = len(y.shape) == 2 and y.shape[0] == 2

        if is_stereo:
            left_channel = y[0]
            right_channel = y[1]
            rms_total = np.sqrt(np.mean((left_channel + right_channel) ** 2)) / 2
        else:
            rms_total = np.sqrt(np.mean(y ** 2))

        if rms_total == 0:
            logging.error("❌ RMS 계산 중 값이 0이 됨!")
            return {"error": "RMS 계산 오류"}

        rms_spl = 20 * np.log10(rms_total / SPL_REFERENCE + 1e-6)
        peak_amplitude = np.max(np.abs(y))
        peak_spl = 20 * np.log10(peak_amplitude / SPL_REFERENCE + 1e-6)

        spl_used = peak_spl if predicted_label in ["차량 경적", "이륜차 경적", "사이렌"] else rms_spl
        db_ref = DB_REFERENCE.get(predicted_label, 85)
        estimated_distance = round(1 * (10 ** ((db_ref - spl_used) / 20)), 2)
        estimated_distance = max(0.1, min(estimated_distance, 1000))

        direction = "알 수 없음"
        if is_stereo:
            rms_left = np.sqrt(np.mean(left_channel ** 2))
            rms_right = np.sqrt(np.mean(right_channel ** 2))
            spl_left = 20 * np.log10(rms_left / SPL_REFERENCE + 1e-6)
            spl_right = 20 * np.log10(rms_right / SPL_REFERENCE + 1e-6)
            db_difference = spl_left - spl_right
            if abs(db_difference) < 1.5:
                direction = "중앙"
            elif 1.5 <= abs(db_difference) < 3:
                direction = "약간 왼쪽" if db_difference > 0 else "약간 오른쪽"
            else:
                direction = "왼쪽" if db_difference > 0 else "오른쪽"
        
        return {
            "prediction": predicted_label,
            "spl": round(spl_used, 2),
            "estimated_distance": estimated_distance,
            "direction": direction,
        }
    except Exception as e:
        logging.error(f"❌ 예외 발생: {str(e)}")
        return {"error": str(e)}

# 🔹 FastAPI 엔드포인트
def predict_label(features):
    predictions = resnet_model.predict(features)
    logging.debug(f"🔍 모델 예측 결과: {predictions}")
    predicted_index = np.argmax(predictions)
    if predicted_index >= len(NOISE_LABELS):
        predicted_index = len(NOISE_LABELS) - 1  # 범위 벗어나는 경우 방어 코드 추가
    predicted_label = NOISE_LABELS[predicted_index]
    logging.debug(f"✅ 최종 예측된 소음 유형: {predicted_label}")
    return predicted_label

@app.post("/predict/")
async def predict(file: UploadFile = File(...)):
    file_bytes = await file.read()
    features = extract_mfcc(file_bytes)
    predicted_label = predict_label(features)
    result = analyze_audio(file_bytes, predicted_label)
    return result


