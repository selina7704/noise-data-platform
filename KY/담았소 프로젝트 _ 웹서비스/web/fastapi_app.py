import logging
import io
import numpy as np
import librosa
import tensorflow as tf
from fastapi import FastAPI, File, UploadFile

app = FastAPI()
logging.basicConfig(level=logging.DEBUG)

# 🔹 모델 로드
def load_model():
    """ ResNet 모델 로드 """
    try:
        model = tf.keras.models.load_model("resnet_model_modified_v6.h5")
        logging.info("✅ 모델 로드 성공")
        return model
    except Exception as e:
        logging.error(f"❌ 모델 로드 실패: {str(e)}")
        return None

resnet_model = load_model()

# 🔹 소음 유형별 기준 데시벨 설정
SPL_REFERENCE = 20e-6  # 0dB 기준 음압
DB_REFERENCE = {
    "차량 경적": 100,
    "이륜차 경적": 100,
    "사이렌": 110,
    "차량 주행음": 90,
    "이륜차 주행음": 95,
    "기타 소음": 85,
}

NOISE_LABELS = ["이륜차 경적", "이륜차 주행음", "차량 경적", "사이렌", "차량 주행음", "기타 소음"]

# 🔹 고주파 소음 목록 (Peak SPL 사용)
HIGH_FREQ_SOUNDS = ["사이렌", "차량 경적", "이륜차 경적"]

# 🔹 MFCC 특징 추출
def extract_mfcc(file_bytes, n_mfcc=50):
    """ 오디오 파일에서 MFCC 특징 추출 """
    y, sr = librosa.load(io.BytesIO(file_bytes), sr=None)
    mfccs = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=n_mfcc)
    return np.mean(mfccs, axis=1).reshape(1, -1)

# 🔹 소음 분류 모델 예측
def predict_label(features, threshold=0.8):
    if resnet_model is None:
        logging.error("❌ 모델이 로드되지 않았음!")
        return "기타 소음"

    predictions = resnet_model.predict(features)
    max_prob = np.max(predictions)
    predicted_index = np.argmax(predictions)

    return NOISE_LABELS[predicted_index] if max_prob >= threshold else "기타 소음"

# 🔹 거리 계산 함수 (소음 유형별 Peak SPL vs RMS SPL 적용)
def estimate_distance(spl_peak, spl_rms, predicted_label):
    """ 소음 유형별 거리 계산 (Peak vs RMS 적용) """
    db_ref = DB_REFERENCE.get(predicted_label, 85)

    # 🔥 Peak SPL을 사용할지, RMS SPL을 사용할지 결정
    if predicted_label in HIGH_FREQ_SOUNDS:
        spl_used = spl_peak
    else:
        spl_used = spl_rms

    estimated_distance = 1 * (10 ** ((db_ref - spl_used) / 20))
    return "50미터 이상" if estimated_distance > 50 else round(estimated_distance, 1)

# 🔹 방향 판별 함수
def estimate_direction(y, predicted_label):
    """ 소음 유형에 따라 고주파/저주파 차이를 반영한 방향 판별 """
    if len(y.shape) == 1:
        return "알 수 없음"

    left_channel, right_channel = y[0], y[1]
    rms_left = np.sqrt(np.mean(left_channel ** 2))
    rms_right = np.sqrt(np.mean(right_channel ** 2))

    spl_left = 20 * np.log10(rms_left / SPL_REFERENCE + 1e-6)
    spl_right = 20 * np.log10(rms_right / SPL_REFERENCE + 1e-6)

    db_diff = spl_left - spl_right
    threshold = 2 if predicted_label in HIGH_FREQ_SOUNDS else 1  

    if abs(db_diff) < threshold:
        return "중앙"
    elif db_diff > threshold:
        return "왼쪽"
    return "오른쪽"

# 🔹 오디오 분석 (데시벨, 거리, 방향 포함)
def analyze_audio(file_bytes, predicted_label):
    """ 오디오 분석 (데시벨, 거리, 방향 포함) """
    y, sr = librosa.load(io.BytesIO(file_bytes), sr=None, mono=False)
    if y is None or len(y) == 0:
        return {"error": "오디오 데이터를 로드하지 못함"}

    is_stereo = len(y.shape) == 2 and y.shape[0] == 2

    # 🔹 RMS & Peak SPL 계산
    rms_total = np.sqrt(np.mean(y ** 2))
    rms_spl = 20 * np.log10(rms_total / SPL_REFERENCE + 1e-6)
    peak_amplitude = np.max(np.abs(y))
    peak_spl = 20 * np.log10(peak_amplitude / SPL_REFERENCE + 1e-6)

    # 🔹 거리 예측 (소음 유형별 SPL 선택)
    estimated_distance = estimate_distance(peak_spl, rms_spl, predicted_label)

    # 🔹 방향 판별
    direction = estimate_direction(y, predicted_label) if is_stereo else "알 수 없음"

    return {
        "prediction": predicted_label,
        "spl_peak": round(peak_spl, 2),
        "spl_rms": round(rms_spl, 2),
        "estimated_distance": estimated_distance,
        "direction": direction
    }

# 🔹 FastAPI 엔드포인트
@app.post("/predict/")
async def predict(file: UploadFile = File(...)):
    """ WAV 파일 분석 API """
    file_bytes = await file.read()
    features = extract_mfcc(file_bytes)
    predicted_label = predict_label(features)
    result = analyze_audio(file_bytes, predicted_label)
    return result


















