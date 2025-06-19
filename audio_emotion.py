from pyAudioAnalysis import audioSegmentation as aS
from pyAudioAnalysis import audioBasicIO
import os

def detect_emotion_from_voice(audio_path):
    try:
        [Fs, x] = audioBasicIO.read_audio_file(audio_path)
        segments, classes, accuracy = aS.mt_file_classification(audio_path, 
                                                                "pyAudioAnalysis/data/svmSpeechEmotion", 
                                                                "svm", False)
        if len(classes) > 0:
            return classes[0]
        else:
            return "unknown"
    except Exception as e:
        print("Emotion Detection Error:", e)
        return "unknown"







# import librosa
# import numpy as np
# import joblib

# # Load pretrained model (train it beforehand using RAVDESS or use one I can help create)
# MODEL_PATH = "utils/emotion_model.pkl"

# def extract_features(file_path):
#     audio, sample_rate = librosa.load(file_path, res_type='kaiser_fast')
#     mfccs = np.mean(librosa.feature.mfcc(y=audio, sr=sample_rate, n_mfcc=40).T, axis=0)
#     return mfccs.reshape(1, -1)

# def detect_emotion_from_voice(file_path):
#     try:
#         model = joblib.load(MODEL_PATH)
#         features = extract_features(file_path)
#         emotion = model.predict(features)[0]
#         return emotion
#     except Exception as e:
#         print("Emotion detection error:", e)
#         return "Unknown"
