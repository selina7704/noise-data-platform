# from flask import Flask, request, jsonify, render_template

# app = Flask(__name__)

# @app.route('/')
# def index():
#     return render_template('index.html')  # index.html 렌더링

# @app.route('/noise', methods=['POST'])
# def noise_detection():
#     data = request.get_json()
#     volume = data.get('volume', 0)

#     # 간단한 소음 감지 예시
#     if volume > 30:
#         return jsonify({"message": "큰 소음 감지!"}), 200
#     else:
#         return jsonify({"message": "소음 없음"}), 200

# if __name__ == '__main__':
#     app.run(debug=True, host='0.0.0.0', port=5000)


from flask import Flask, request, jsonify, render_template
import tensorflow as tf
import numpy as np
import librosa

# GPU 비활성화 (CPU로만 실행)
tf.config.set_visible_devices([], 'GPU')

# resnet 모델 
#model = tf.keras.models.load_model('../ES/resnet_model_mfcc50.h5')  
model = tf.keras.models.load_model('../ES/cnn_model_6classfication.h5')

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/noise', methods=['POST'])
def noise_detection():
    data = request.get_json()
    volume = data.get('volume', 0)

    # 오디오 데이터를 받아서 MFCC로 변환 후 예측 수행
    audio_data = np.array([volume])  # 예시로 volume을 사용, 실제 오디오 데이터로 처리 필요
    features = extract_mfcc(audio_data)  # MFCC 추출 함수

    # 모델 예측
    prediction = model.predict(np.array([features]))  # 예측된 소음 유형
    predicted_label = np.argmax(prediction)  # 예측된 클래스 (소음 종류)

    # 예측된 라벨을 터미널에 출력
    noise_labels = ['이륜차경적', '이륜차주행음', '차량경적', '차량사이렌', '차량주행음']
    print(f"예측된 소음 유형: {noise_labels[predicted_label]}")  # 터미널에 출력

    # 예측 결과 반환
    return jsonify({"message": f"{noise_labels[predicted_label]} 감지!"}), 200
def extract_mfcc(audio_data, n_mfcc=50):
    mfccs = librosa.feature.mfcc(y=audio_data, sr=22050, n_mfcc=n_mfcc)
    return np.mean(mfccs, axis=1)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)