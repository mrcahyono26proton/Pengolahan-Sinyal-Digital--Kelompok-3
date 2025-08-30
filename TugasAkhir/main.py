import tkinter as tk
from tkinter import filedialog, messagebox
import numpy as np
import librosa
import joblib
import os
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# Load Dataset & Train
DATASET_DIR = "speech_commands_v0.02"
TARGET_LABELS = ["down", "left", "right"]

def extract_features(file_path):
    y, sr = librosa.load(file_path, sr=16000)
    mfcc = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)
    return np.mean(mfcc.T, axis=0)

X, y = [], []
for label in TARGET_LABELS:
    folder = os.path.join(DATASET_DIR, label)
    if not os.path.exists(folder):
        continue
    for file in os.listdir(folder)[:100]:
        fpath = os.path.join(folder, file)
        feat = extract_features(fpath)
        X.append(feat)
        y.append(label)

X = np.array(X)
y = np.array(y)

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
model = LogisticRegression(max_iter=1000)
model.fit(X_train, y_train)

print("Akurasi:", model.score(X_test, y_test))
clf = model

# Buat komponen GUI
root = tk.Tk()
root.title("Speech Command Inference")

frame = tk.Frame(root, padx=20, pady=20)
frame.pack()

btn_load = tk.Button(frame, text="Pilih File Audio", command=lambda: predict_file(canvas, ax1, ax2))
btn_load.pack(pady=10)

result_label = tk.Label(frame, text="Prediksi: -", font=("Arial", 14))
result_label.pack(pady=10)

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(9, 4))
fig.tight_layout(pad=3.0)

canvas = FigureCanvasTkAgg(fig, master=root)
canvas_widget = canvas.get_tk_widget()
canvas_widget.pack()

def predict_file(canvas, ax1, ax2):
    file_path = filedialog.askopenfilename(filetypes=[("WAV files", "*.wav")])
    if not file_path:
        return
    
    # Ekstraksi fitur dan prediksi
    y_audio, sr_audio = librosa.load(file_path, sr=16000)
    feat = extract_features(file_path).reshape(1, -1)
    
    # Prediksi
    pred = clf.predict(feat)[0]
    result_label.config(text=f"Prediksi: {pred}")

    ax1.clear()
    ax2.clear()

    # Plot Sinyal Domain Waktu
    librosa.display.waveshow(y_audio, sr=sr_audio, ax=ax1)
    ax1.set_title("Sinyal Audio (Domain Waktu)")
    ax1.set_xlabel("Waktu")
    ax1.set_ylabel("Amplitudo")
    ax1.grid(True)

    # Plot Sinyal FFT
    N = len(y_audio)
    fft_result = np.fft.fft(y_audio)
    fft_magnitude = np.abs(fft_result)
    frequencies = np.fft.fftfreq(N, 1/sr_audio)

    positive_freq_mask = frequencies >= 0
    ax2.plot(frequencies[positive_freq_mask], fft_magnitude[positive_freq_mask])
    ax2.set_title("Spektrum Frekuensi FFT")
    ax2.set_xlabel("Frekuensi")
    ax2.set_ylabel("Magnitudo")
    ax2.grid(True)

    canvas.draw()

root.mainloop()