import librosa
import numpy as np

def detect_emotion_from_voice(file_path):
    y, sr = librosa.load(file_path)
    energy = np.mean(np.square(y))

    # Dummy rule-based emotion detection based on energy level
    if energy < 0.01:
        return "Calm"
    elif energy < 0.03:
        return "Neutral"
    else:
        return "Excited"






















# from pyAudioAnalysis import audioSegmentation as aS
# from pyAudioAnalysis import audioBasicIO
# import os

# def detect_emotion_from_voice(audio_path):
#     try:
#         [Fs, x] = audioBasicIO.read_audio_file(audio_path)
#         segments, classes, accuracy = aS.mt_file_classification(audio_path, 
#                                                                 "pyAudioAnalysis/data/svmSpeechEmotion", 
#                                                                 "svm", False)
#         if len(classes) > 0:
#             return classes[0]
#         else:
#             return "unknown"
#     except Exception as e:
#         print("Emotion Detection Error:", e)
#         return "unknown"

