import os
import sys
import time
import traceback
import threading
import tkinter as tk
from tkinter import ttk, messagebox, filedialog

import numpy as np
import sounddevice as sd
from scipy.io.wavfile import write as wav_write, read as wav_read

import matplotlib
matplotlib.use("TkAgg")
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


# ===================== Parameters =====================
SAMPLE_RATE = 44100
MAX_SECONDS = 4                # Max recording duration (seconds)
RECORD_FILE = os.path.abspath("record.wav")

DFT_MAX_POINTS = 4096          # DFT processes only first N points (O(N^2) cost)
PLOT_MAX_FREQ = 5000           # Only plot 0 ~ 5 kHz

# UI font
UI_FONT_FAMILY = 'DejaVu Sans'
UI_FONT_SIZE = 16
UI_SCALING = 1.4


# ===================== Logging =====================
def log(*args):
    msg = " ".join(str(a) for a in args)
    print(f"[{time.strftime('%H:%M:%S')}] {msg}", flush=True)


def log_devices():
    log("=" * 60)
    log("Audio devices:")
    try:
        devices = sd.query_devices()
        for i, d in enumerate(devices):
            log(f"  [{i}] {d['name']}  "
                f"in={d['max_input_channels']} out={d['max_output_channels']} "
                f"default_sr={d['default_samplerate']}")
        log("-" * 60)
        default_in, default_out = sd.default.device
        log(f"Default input index : {default_in}")
        log(f"Default output index: {default_out}")
        if default_in is not None and default_in >= 0:
            log(f"Default input name  : {devices[default_in]['name']}")
        else:
            log("WARNING: No default input device available. Check microphone.")
    except Exception as e:
        log("Failed to query devices:", e)
        traceback.print_exc()
    log("=" * 60)


# ===================== Main App =====================
class AudioApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Audio Recorder & Spectrum Analyzer (Wave / FFT / DFT)")
        self.root.geometry("1000x780")

        self.audio = None
        self.fs = SAMPLE_RATE
        self.is_recording = False
        self.record_thread = None
        self.frames_written = 0

        self.record_buffer = np.zeros(int(MAX_SECONDS * SAMPLE_RATE), dtype=np.float32)

        self._build_ui()
        self.root.after(200, self._print_startup_info)

    def _print_startup_info(self):
        log_devices()
        self._check_default_input()

    def _check_default_input(self):
        try:
            default_in, _ = sd.default.device
            devices = sd.query_devices()
            if default_in is None or default_in < 0:
                self.status.set("WARNING: No default input device")
                log("WARNING: No default input device")
                return
            if devices[default_in]['max_input_channels'] < 1:
                self.status.set(f"WARNING: Default device [{default_in}] is not an input")
                log(f"WARNING: Default device [{default_in}] "
                    f"{devices[default_in]['name']} is not an input device")
        except Exception as e:
            log("Failed to check default input device:", e)

    # ---------------- UI ----------------
    def _build_ui(self):
        # ---- Enlarge ttk widget font ----
        style = ttk.Style()
        ui_font = (UI_FONT_FAMILY, UI_FONT_SIZE)
        style.configure('TButton', font=ui_font, padding=(12, 8))
        style.configure('TLabel',  font=ui_font)
        style.configure('TFrame',  font=ui_font)
        style.configure('TProgressbar', thickness=18)

        top = ttk.Frame(self.root, padding=8)
        top.pack(fill=tk.X)

        self.btn_record = ttk.Button(top, text="Start Recording (<=4s)",
                                     command=self.toggle_record)
        self.btn_record.pack(side=tk.LEFT, padx=4)

        self.btn_load = ttk.Button(top, text="Load WAV",
                                   command=self.load_wav)
        self.btn_load.pack(side=tk.LEFT, padx=4)

        self.btn_analyze = ttk.Button(top, text="Analyze (Wave / FFT / DFT)",
                                      command=self.analyze)
        self.btn_analyze.pack(side=tk.LEFT, padx=4)

        self.btn_devices = ttk.Button(top, text="Devices",
                                      command=log_devices)
        self.btn_devices.pack(side=tk.LEFT, padx=4)

        self.status = tk.StringVar(value="Ready")
        ttk.Label(top, textvariable=self.status).pack(side=tk.LEFT, padx=12)

        self.progress = ttk.Progressbar(top, length=150, maximum=MAX_SECONDS)
        self.progress.pack(side=tk.RIGHT, padx=6)

        # ---- Figure area ----
        self.fig = Figure(figsize=(10, 7), dpi=100)
        self.ax_wave = self.fig.add_subplot(3, 1, 1)
        self.ax_fft  = self.fig.add_subplot(3, 1, 2)
        self.ax_dft  = self.fig.add_subplot(3, 1, 3)

        for ax in (self.ax_wave, self.ax_fft, self.ax_dft):
            ax.title.set_fontsize(14)
            ax.xaxis.label.set_fontsize(12)
            ax.yaxis.label.set_fontsize(12)
            ax.tick_params(labelsize=10)

        self.ax_wave.set_title("Waveform (Amplitude)")
        self.ax_fft.set_title("FFT Spectrum")
        self.ax_dft.set_title("DFT Spectrum")
        self.fig.tight_layout()

        self.canvas = FigureCanvasTkAgg(self.fig, master=self.root)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    # ---------------- Recording ----------------
    def toggle_record(self):
        if not self.is_recording:
            self.start_record()
        else:
            self.stop_record()

    def start_record(self):
        try:
            default_in, _ = sd.default.device
            devices = sd.query_devices()
            if default_in is None or default_in < 0:
                messagebox.showerror("Error",
                                     "No input device (microphone) available.")
                return
            if devices[default_in]['max_input_channels'] < 1:
                messagebox.showerror("Error",
                                     f"Default device [{default_in}] "
                                     f"{devices[default_in]['name']} "
                                     f"is not an input device.")
                return
            log(f"Using input device [{default_in}] {devices[default_in]['name']}")
        except Exception as e:
            log("Device check failed:", e)
            traceback.print_exc()

        self.is_recording = True
        self.frames_written = 0
        self.record_buffer[:] = 0
        self.progress['value'] = 0
        self.btn_record.config(text="Stop Recording")
        self.status.set("Recording...")
        log(">> Start recording")

        self.record_thread = threading.Thread(target=self._record_worker, daemon=True)
        self.record_thread.start()
        self._update_progress()

    def _record_worker(self):
        def callback(indata, frames, time_info, status):
            if status:
                log("WARNING: recording status:", status)
            if self.frames_written + frames > len(self.record_buffer):
                log("Max recording length reached, stopping automatically")
                raise sd.CallbackStop()
            self.record_buffer[self.frames_written:self.frames_written + frames] = indata[:, 0]
            self.frames_written += frames

        try:
            with sd.InputStream(
                samplerate=SAMPLE_RATE,
                channels=1,
                dtype="float32",
                callback=callback,
                blocksize=1024,
            ):
                log("InputStream opened, recording...")
                while self.is_recording and self.frames_written < len(self.record_buffer):
                    sd.sleep(50)
        except Exception as e:
            log("ERROR: recording exception:", e)
            traceback.print_exc()
            self.root.after(0, lambda: messagebox.showerror(
                "Recording error", f"{e}\n\nSee console log."))
        finally:
            self.root.after(0, self._finalize_record)

    def stop_record(self):
        self.is_recording = False
        self.status.set("Stopping...")
        log("|| User requested stop")

    def _finalize_record(self):
        self.btn_record.config(text="Start Recording (<=4s)")
        n = self.frames_written
        log(f"Recording finished, {n} samples ({n / SAMPLE_RATE:.2f} s)")

        if n == 0:
            self.status.set("WARNING: No audio captured")
            log("WARNING: No audio captured")
            messagebox.showwarning("Notice",
                                   "No audio captured.\nSee console log.")
            return

        audio = self.record_buffer[:n].copy()
        self.audio = audio
        self.fs = SAMPLE_RATE

        try:
            peak = np.max(np.abs(audio))
            audio_norm = audio / peak if peak > 1.0 else audio
            pcm = (audio_norm * 32767).astype(np.int16)
            wav_write(RECORD_FILE, SAMPLE_RATE, pcm)

            if os.path.exists(RECORD_FILE):
                size = os.path.getsize(RECORD_FILE)
                log(f"Saved: {RECORD_FILE}  ({size} bytes)")
                self.status.set(f"Done: {n / SAMPLE_RATE:.2f} s -> {RECORD_FILE}")
            else:
                log("ERROR: wav file does not exist after write!")
                self.status.set("ERROR: save failed")
        except Exception as e:
            log("ERROR: failed to save wav:", e)
            traceback.print_exc()
            self.status.set("ERROR: save failed, see console")
            messagebox.showerror("Save failed", f"{e}\n\nPath: {RECORD_FILE}")

    def _update_progress(self):
        if self.is_recording:
            sec = self.frames_written / SAMPLE_RATE
            self.progress['value'] = min(sec, MAX_SECONDS)
            self.root.after(100, self._update_progress)
        else:
            self.progress['value'] = 0

    # ---------------- Load WAV ----------------
    def load_wav(self):
        path = RECORD_FILE
        if not os.path.exists(path):
            log(f"{path} not found, opening file dialog")
            path = filedialog.askopenfilename(filetypes=[("WAV", "*.wav")])
            if not path:
                return

        try:
            fs, data = wav_read(path)
            log(f"Read {path}: fs={fs}, shape={data.shape}, dtype={data.dtype}")
            if data.ndim > 1:
                data = data.mean(axis=1)
            if data.dtype == np.int16:
                data = data.astype(np.float32) / 32768.0
            else:
                data = data.astype(np.float32)

            max_len = int(fs * MAX_SECONDS)
            if len(data) > max_len:
                data = data[:max_len]

            self.fs = fs
            self.audio = data
            self.status.set(f"Loaded: {os.path.basename(path)}, "
                            f"{len(data)/fs:.2f} s")
            log(f"Loaded successfully, {len(data)} samples")
        except Exception as e:
            log("ERROR: load failed:", e)
            traceback.print_exc()
            messagebox.showerror("Load error", str(e))

    # ---------------- Analyze ----------------
    def analyze(self):
        if self.audio is None or len(self.audio) == 0:
            messagebox.showwarning("Notice",
                                   "Please record or load a WAV file first.")
            return

        log("Analyzing...")
        self.status.set("Computing Wave / FFT / DFT ...")
        self.root.update_idletasks()

        x = self.audio.astype(np.float32)
        fs = self.fs
        t = np.arange(len(x)) / fs

        # ---------- Waveform ----------
        self.ax_wave.clear()
        self.ax_wave.plot(t, x, linewidth=0.6)
        self.ax_wave.set_title("Waveform (Amplitude)")
        self.ax_wave.set_xlabel("Time (s)")
        self.ax_wave.set_ylabel("Amplitude")
        self.ax_wave.grid(True, alpha=0.3)

        # ---------- FFT ----------
        N = len(x)
        fft_vals = np.fft.rfft(x)
        fft_mag = np.abs(fft_vals) / N * 2
        fft_freqs = np.fft.rfftfreq(N, d=1.0 / fs)
        mask = fft_freqs <= PLOT_MAX_FREQ
        self.ax_fft.clear()
        self.ax_fft.plot(fft_freqs[mask], fft_mag[mask],
                         linewidth=0.7, color="tab:orange")
        self.ax_fft.set_title(f"FFT Spectrum (N={N})")
        self.ax_fft.set_xlabel("Frequency (Hz)")
        self.ax_fft.set_ylabel("Magnitude")
        self.ax_fft.grid(True, alpha=0.3)

        # ---------- DFT (Scheme B: first N points, no decimation) ----------
        seg = x[:DFT_MAX_POINTS] if len(x) > DFT_MAX_POINTS else x
        M = len(seg)
        seg_ms = M / fs * 1000.0
        resolution = fs / M
        log(f"DFT uses first {M} points (~{seg_ms:.1f} ms), "
            f"resolution {resolution:.2f} Hz")

        t0 = time.time()
        dft_vals = self._dft(seg)
        dt = time.time() - t0
        log(f"DFT compute time {dt*1000:.1f} ms")

        dft_mag = np.abs(dft_vals) / M * 2
        dft_freqs = np.fft.fftfreq(M, d=1.0 / fs)

        half = M // 2
        dft_freqs_pos = dft_freqs[:half]
        dft_mag_pos = dft_mag[:half]

        mask2 = dft_freqs_pos <= PLOT_MAX_FREQ
        self.ax_dft.clear()
        self.ax_dft.plot(dft_freqs_pos[mask2], dft_mag_pos[mask2],
                         linewidth=0.7, color="tab:green")
        self.ax_dft.set_title(f"DFT Spectrum (N={M}, first {seg_ms:.0f} ms)")
        self.ax_dft.set_xlabel("Frequency (Hz)")
        self.ax_dft.set_ylabel("Magnitude")
        self.ax_dft.grid(True, alpha=0.3)

        self.fig.tight_layout()
        self.canvas.draw()

        self.status.set(f"Done: FFT {N} pts, DFT {M} pts ({dt*1000:.0f} ms)")
        log("Analysis complete")

    @staticmethod
    def _dft(x):
        """Naive O(N^2) DFT, accelerated by NumPy matrix multiplication"""
        x = np.asarray(x, dtype=np.complex128)
        N = len(x)
        n = np.arange(N)
        k = n.reshape((N, 1))
        W = np.exp(-2j * np.pi * k * n / N)
        return np.dot(W, x)


if __name__ == "__main__":
    log("Program started")
    log(f"Python     : {sys.version}")
    log(f"sounddevice: {sd.__version__}")
    log(f"numpy      : {np.__version__}")
    log(f"Working dir: {os.getcwd()}")
    log(f"Target file: {RECORD_FILE}")
    log(f"MAX_SECONDS = {MAX_SECONDS}, DFT_MAX_POINTS = {DFT_MAX_POINTS}")

    root = tk.Tk()
    root.tk.call('tk', 'scaling', UI_SCALING)
    app = AudioApp(root)
    root.mainloop()
    log("Program exited")
