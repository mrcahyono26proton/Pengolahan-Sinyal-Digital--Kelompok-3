import tkinter as tk
from tkinter import filedialog, messagebox
import soundfile as sf
import numpy as np
from scipy import signal
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import sounddevice as sd
import threading
import time

class AudioProcessorApp:
    def __init__(self, master):
        self.master = master
        master.title("Mini Proyek: Reduksi Noise Audio")
        master.geometry("1000x950")

        self.original_audio = None
        self.noisy_audio = None
        self.denoised_audio = None
        self.samplerate = None

        self.current_playback_stream = None
        self.playback_thread = None
        self.is_playing = False
        self.playback_lock = threading.Lock()

        # Frame tombol tambah audio
        self.process_control_frame = tk.Frame(master, bd=2, relief="groove", padx=10, pady=10)
        self.process_control_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=5)

        self.load_button = tk.Button(self.process_control_frame, text="Muat Audio.wav", command=self.load_and_process_audio,
                                     font=("Roboto", 10, "bold"), bg="#4CAF50", fg="white", relief="raised")
        self.load_button.pack(padx=5, pady=5, fill=tk.X)

        # Frame untuk pemutaran audio
        self.playback_category_frame = tk.Frame(master, bd=2, relief="groove", padx=10, pady=10)
        self.playback_category_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=5)

        # Kontrol untuk audio asli
        tk.Label(self.playback_category_frame, text="Audio Asli:", font=("Roboto", 10, "bold")).grid(row=0, column=0, padx=5, pady=2, sticky="w")
        self.play_original_button = tk.Button(self.playback_category_frame, text="► Putar Audio Asli", command=self.play_original_audio, state=tk.DISABLED,
                                               font=("Roboto", 10), bg="#008CBA", fg="white", relief="raised")
        self.play_original_button.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        # Kontrol untuk audio noise
        tk.Label(self.playback_category_frame, text="Audio Noise:", font=("Roboto", 10, "bold")).grid(row=1, column=0, padx=5, pady=2, sticky="w")
        self.play_noisy_button = tk.Button(self.playback_category_frame, text="► Putar Audio Noise", command=self.play_noisy_audio, state=tk.DISABLED,
                                            font=("Roboto", 10), bg="#008CBA", fg="white", relief="raised")
        self.play_noisy_button.grid(row=1, column=1, padx=5, pady=5, sticky="ew")

        # Kontrol untuk audio filter
        tk.Label(self.playback_category_frame, text="Audio Filter:", font=("Roboto", 10, "bold")).grid(row=2, column=0, padx=5, pady=2, sticky="w")
        self.play_denoised_button = tk.Button(self.playback_category_frame, text="► Putar Audio Filter", command=self.play_denoised_audio, state=tk.DISABLED,
                                               font=("Roboto", 10), bg="#008CBA", fg="white", relief="raised")
        self.play_denoised_button.grid(row=2, column=1, padx=5, pady=5, sticky="ew")

        # Mengatur kolom
        self.playback_category_frame.grid_columnconfigure(0, weight=0)
        self.playback_category_frame.grid_columnconfigure(1, weight=1)

        # --- Frame untuk Plot ---
        self.plot_frame = tk.Frame(master, bd=2, relief="groove")
        self.plot_frame.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.fig, ((self.ax_orig_time, self.ax_orig_freq),
                   (self.ax_noisy_time, self.ax_noisy_freq),
                   (self.ax_denoised_time, self.ax_denoised_freq)) = plt.subplots(3, 2, figsize=(9, 8))
        
        self.fig.suptitle("Visualisasi Sinyal Audio dan Spektrum Frekuensi", fontsize=14, fontweight='bold')
        plt.tight_layout(rect=[0, 0.03, 1, 0.96])

        self.canvas = FigureCanvasTkAgg(self.fig, master=self.plot_frame)
        self.canvas_widget = self.canvas.get_tk_widget()
        self.canvas_widget.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        self.toolbar = NavigationToolbar2Tk(self.canvas, self.plot_frame)
        self.toolbar.update()
        self.canvas_widget.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        self.master.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.plot_all_audio()

    def on_closing(self):
        self.stop_playback()
        self.master.destroy()

    def load_and_process_audio(self):
        self.stop_playback()
        try:
            file_path = filedialog.askopenfilename(filetypes=[("WAV files", "*.wav")])
            if not file_path:
                return

            self.original_audio, self.samplerate = sf.read(file_path)

            if self.original_audio.ndim > 1:
                self.original_audio = self.original_audio.mean(axis=1)

            noise_amplitude = 0.15 * np.max(np.abs(self.original_audio))
            noise = noise_amplitude * np.random.randn(len(self.original_audio))
            self.noisy_audio = self.original_audio + noise

            cutoff_freq = 3500 # Hz
            nyquist_freq = 0.5 * self.samplerate
            normalized_cutoff = cutoff_freq / nyquist_freq
            order = 5

            b, a = signal.butter(order, normalized_cutoff, btype='low', analog=False)
            self.denoised_audio = signal.lfilter(b, a, self.noisy_audio)

            self.play_original_button.config(state=tk.NORMAL)
            self.play_noisy_button.config(state=tk.NORMAL)
            self.play_denoised_button.config(state=tk.NORMAL)

            self.plot_all_audio()

        except Exception as e:
            messagebox.showerror("Error", f"Gagal memuat atau memproses audio: {e}\nPastikan file WAV valid.")
            self.reset_app_state()

    def plot_all_audio(self):
        for ax_row in self.fig.axes:
            ax_row.clear()

        # Helper function
        def plot_single_audio(audio_data, time_ax, freq_ax, title_prefix, color_time='blue', color_freq='red'):
            if audio_data is None or self.samplerate is None:
                time_ax.set_title(f"{title_prefix} (Tidak Ada Data)", fontsize=10, fontweight='bold', color='gray')
                freq_ax.set_title(f"Spektrum {title_prefix} (Tidak Ada Data)", fontsize=10, fontweight='bold', color='gray')
                time_ax.set_xticks([])
                time_ax.set_yticks([])
                freq_ax.set_xticks([])
                freq_ax.set_yticks([])
                return

            # Plot Domain Waktu
            time = np.linspace(0, len(audio_data) / self.samplerate, len(audio_data))
            time_ax.plot(time, audio_data, color=color_time)
            time_ax.set_title(f"{title_prefix} (Domain Waktu)", fontsize=10, fontweight='bold')
            time_ax.set_xlabel("Waktu (detik)", fontsize=8)
            time_ax.set_ylabel("Amplitudo", fontsize=8)
            time_ax.grid(True, linestyle='--', alpha=0.7)

            # Plot Domain Frekuensi FFT
            N = len(audio_data)
            yf = np.fft.fft(audio_data)
            xf = np.fft.fftfreq(N, 1 / self.samplerate)
            positive_freq_idx = np.where(xf >= 0)
            freq_ax.plot(xf[positive_freq_idx], 2.0/N * np.abs(yf[positive_freq_idx]), color=color_freq)
            freq_ax.set_title(f"Spektrum {title_prefix} (Domain Frekuensi)", fontsize=10, fontweight='bold')
            freq_ax.set_xlabel("Frekuensi (Hz)", fontsize=8)
            freq_ax.set_ylabel("Magnitude", fontsize=8)
            freq_ax.set_xlim(0, self.samplerate / 2)
            freq_ax.grid(True, linestyle='--', alpha=0.7)

        # Plot Original Audio
        plot_single_audio(self.original_audio, self.ax_orig_time, self.ax_orig_freq, "Audio Asli", 'blue', 'red')

        # Plot Noisy Audio
        plot_single_audio(self.noisy_audio, self.ax_noisy_time, self.ax_noisy_freq, "Audio Noise", 'orange', 'purple')

        # Plot Audio Filter
        plot_single_audio(self.denoised_audio, self.ax_denoised_time, self.ax_denoised_freq, "Audio Filter", 'green', 'darkgreen')

        self.fig.tight_layout(rect=[0, 0.03, 1, 0.96]) 
        self.canvas.draw()

    def _play_audio_thread(self, audio_data, samplerate):
        stream_local = None
        try:
            with self.playback_lock:
                if self.current_playback_stream and self.current_playback_stream.active:
                    self.current_playback_stream.stop()
                    if not self.current_playback_stream.closed:
                        self.current_playback_stream.close()
                self.current_playback_stream = None
                self.is_playing = True

                stream_local = sd.play(audio_data, samplerate, blocking=False)
                self.current_playback_stream = stream_local

            if stream_local is not None:
                stream_local.wait()

            with self.playback_lock:
                if self.current_playback_stream is stream_local and (stream_local is None or not stream_local.active):
                    self.is_playing = False
                    if stream_local and not stream_local.closed:
                        stream_local.close()
                    self.current_playback_stream = None
                elif self.current_playback_stream is not stream_local:
                    if stream_local and not stream_local.closed:
                        stream_local.close()

        except Exception as e:
            
            with self.playback_lock:
                self.is_playing = False
                if stream_local and not stream_local.closed:
                    stream_local.close()
                if self.current_playback_stream is stream_local:
                    self.current_playback_stream = None


    def start_playback(self, audio_data):
        if audio_data is None or self.samplerate is None:
            messagebox.showwarning("Peringatan", "Tidak ada audio untuk diputar.")
            return

        self.stop_playback() 
        time.sleep(0.05)

        if self.playback_thread and self.playback_thread.is_alive():
            self.playback_thread.join(timeout=0.1) 

        self.playback_thread = threading.Thread(target=self._play_audio_thread,
                                                args=(audio_data, self.samplerate))
        self.playback_thread.daemon = True
        self.playback_thread.start()

    def stop_playback(self):
        with self.playback_lock: # Acquire lock to safely stop and clear
            if self.current_playback_stream and self.current_playback_stream.active:
                sd.stop() 
                if not self.current_playback_stream.closed:
                    self.current_playback_stream.close()
                self.current_playback_stream = None 
                self.is_playing = False
            elif self.is_playing:
                self.is_playing = False

        if self.playback_thread and self.playback_thread.is_alive():
            self.playback_thread.join(timeout=0.1)


    def play_original_audio(self):
        self.start_playback(self.original_audio)

    def play_noisy_audio(self):
        self.start_playback(self.noisy_audio)

    def play_denoised_audio(self):
        self.start_playback(self.denoised_audio)

    def reset_app_state(self):
        self.original_audio = None
        self.noisy_audio = None
        self.denoised_audio = None
        self.samplerate = None
        self.stop_playback()
        
        self.play_original_button.config(state=tk.DISABLED)
        self.play_noisy_button.config(state=tk.DISABLED)
        self.play_denoised_button.config(state=tk.DISABLED)

        self.plot_all_audio()


if __name__ == "__main__":
    root = tk.Tk()
    app = AudioProcessorApp(root)
    root.mainloop()
