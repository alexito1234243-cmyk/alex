"""Locución sin conexión con Kokoro (sherpa-onnx). Los modelos se bajan con video/get_voices.sh.

Voces en español: dora (mujer), alex y santa (hombres).
Comprobar pronunciación:  python3 video/voz.py --check "texto a decir"  (necesita get_voices.sh --check)
"""
import os
import re
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
MODELS = os.environ.get("TTS_MODELS", os.path.join(HERE, "models"))
VOICES = {"dora": 28, "alex": 29, "santa": 53}
SR = 44100
LEAD = 0.12  # silencio antes de que empiece a hablar en cada escena


def clean(text):
    text = text.replace("…", ", ").strip(" ,")
    return re.sub(r"\s*,\s*(,\s*)+", ", ", text)


def trim(x, sr, thr=0.01):
    idx = np.where(np.abs(x) > thr)[0]
    if not len(idx):
        return x
    return x[max(0, idx[0] - int(0.03 * sr)): idx[-1] + int(0.08 * sr)]


def resample(x, sr_in, sr_out=SR):
    if sr_in == sr_out:
        return x
    t_out = np.arange(int(len(x) * sr_out / sr_in)) / sr_out
    return np.interp(t_out, np.arange(len(x)) / sr_in, x).astype(np.float32)


class Narrator:
    def __init__(self, voice="dora", speed=1.08, threads=4):
        import sherpa_onnx
        d = os.path.join(MODELS, "kokoro-multi-lang-v1_0")
        if not os.path.isdir(d):
            sys.exit(f"Faltan los modelos de voz en {d}: ejecuta video/get_voices.sh")
        cfg = sherpa_onnx.OfflineTtsConfig(model=sherpa_onnx.OfflineTtsModelConfig(
            kokoro=sherpa_onnx.OfflineTtsKokoroModelConfig(
                model=f"{d}/model.onnx", voices=f"{d}/voices.bin", tokens=f"{d}/tokens.txt",
                data_dir=f"{d}/espeak-ng-data", lang="es"),
            num_threads=threads))
        self.tts = sherpa_onnx.OfflineTts(cfg)
        self.sid = VOICES[voice]
        self.speed = speed

    def say(self, text):
        a = self.tts.generate(clean(text), sid=self.sid, speed=self.speed)
        x = trim(np.asarray(a.samples, dtype=np.float32), a.sample_rate)
        x = resample(x, a.sample_rate)
        return 0.9 * x / (np.max(np.abs(x)) + 1e-9)


def transcribe(samples, sr=SR):
    """Transcribe con Whisper para comprobar que la voz se entiende."""
    import sherpa_onnx
    w = os.path.join(MODELS, "sherpa-onnx-whisper-base")
    rec = sherpa_onnx.OfflineRecognizer.from_whisper(
        encoder=f"{w}/base-encoder.int8.onnx", decoder=f"{w}/base-decoder.int8.onnx",
        tokens=f"{w}/base-tokens.txt", language="es", task="transcribe", num_threads=4)
    s = rec.create_stream()
    s.accept_waveform(sr, samples)
    rec.decode_stream(s)
    return s.result.text.strip()


if __name__ == "__main__":
    if "--check" in sys.argv:
        phrase = sys.argv[sys.argv.index("--check") + 1]
        for name in VOICES:
            print(f"{name}: {transcribe(Narrator(name).say(phrase))}")
