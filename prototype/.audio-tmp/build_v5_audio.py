"""Build the V5 48 s normal-speed scratch mix.

The source is the raw 47.804 s Kevin take used at its natural speed.
The voice is the raw Kevin take (47.804 s), with no time-stretch or slowdown.
The bed is deliberately quiet, so the voice carries every visual beat.
"""

from pathlib import Path
import json
import numpy as np
import soundfile as sf
import pyloudnorm as pyln
from scipy.signal import butter, sosfilt

ROOT = Path("/home/jazzmeen/Documents/JILMONDE/refonte/Refonte site jilms.bj")
TMP = ROOT / ".audio-tmp"
OUT = ROOT / "livrables"
SR = 44100
TOTAL = 48.0
N = int(round(SR * TOTAL))
rng = np.random.default_rng(20261029)


def read_mono(path: Path) -> np.ndarray:
    y, sr = sf.read(path, dtype="float32", always_2d=False)
    if y.ndim > 1:
        y = y.mean(axis=1)
    if sr != SR:
        # The file is already 44.1 kHz; this is a safety net only.
        from scipy.signal import resample_poly
        from math import gcd
        g = gcd(SR, sr)
        y = resample_poly(y, SR // g, sr // g).astype(np.float32)
    return y


def fit(y: np.ndarray, n: int) -> np.ndarray:
    if len(y) < n:
        return np.pad(y, (0, n - len(y))).astype(np.float32)
    return y[:n].astype(np.float32)


def compressor(y: np.ndarray, threshold_db=-24.0, ratio=3.0,
               attack_ms=8.0, release_ms=130.0) -> np.ndarray:
    """Simple one-pole compressor; smooth, no look-ahead, fine for a scratch."""
    eps = 1e-9
    level = 20.0 * np.log10(np.maximum(np.abs(y), eps))
    attack = np.exp(-1.0 / (SR * attack_ms / 1000.0))
    release = np.exp(-1.0 / (SR * release_ms / 1000.0))
    env = np.empty_like(level)
    e = level[0]
    for i, x in enumerate(level):
        coeff = attack if x > e else release
        e = coeff * e + (1.0 - coeff) * x
        env[i] = e
    over = np.maximum(0.0, env - threshold_db)
    gain_db = -over * (1.0 - 1.0 / ratio)
    # Smooth the gain curve to avoid zipper noise.
    g = np.empty_like(gain_db)
    ge = gain_db[0]
    for i, x in enumerate(gain_db):
        coeff = attack if x < ge else release
        ge = coeff * ge + (1.0 - coeff) * x
        g[i] = ge
    return (y * (10.0 ** (g / 20.0))).astype(np.float32)


def peak_limit(y: np.ndarray, ceiling_db=-1.3) -> np.ndarray:
    ceiling = 10.0 ** (ceiling_db / 20.0)
    # Soft knee above 0.86 of the ceiling, then hard safety clip.
    knee = ceiling * 0.86
    a = np.abs(y)
    shaped = np.where(
        a > knee,
        np.sign(y) * (knee + (ceiling - knee) * np.tanh((a - knee) / (ceiling - knee))),
        y,
    )
    return np.clip(shaped, -ceiling, ceiling).astype(np.float32)


def env_ar(n: int, attack: float, release: float) -> np.ndarray:
    """0→1 attack, then 1→0 release, both in seconds."""
    a = max(1, int(attack * SR))
    r = max(1, int(release * SR))
    e = np.ones(n, dtype=np.float32)
    e[:a] = np.linspace(0, 1, a, endpoint=False) ** 2
    e[-r:] *= np.linspace(1, 0, r, endpoint=True) ** 2
    return e


def add_at(dst: np.ndarray, src: np.ndarray, at: float, gain=1.0):
    i = int(round(at * SR))
    if i >= len(dst):
        return
    src = src[: len(dst) - i]
    dst[i:i + len(src)] += src * gain


def make_bed() -> np.ndarray:
    t = np.arange(N) / SR
    bed = np.zeros(N, dtype=np.float32)

    # Very low, breathing room tone.
    lfo = 0.5 + 0.5 * np.sin(2 * np.pi * 0.027 * t - 0.7)
    drone = (
        0.55 * np.sin(2 * np.pi * 55.0 * t)
        + 0.28 * np.sin(2 * np.pi * 82.5 * t + 0.6)
        + 0.12 * np.sin(2 * np.pi * 110.0 * t + 1.9)
    )
    bed += (0.010 + 0.006 * lfo) * drone

    # A barely-there low pulse, like a distant kick every two seconds.
    period = 2.0
    for at in np.arange(0.25, TOTAL, period):
        n = int(0.32 * SR)
        tt = np.arange(n) / SR
        pulse = np.sin(2 * np.pi * 52.0 * tt) * np.exp(-tt * 18.0)
        add_at(bed, pulse.astype(np.float32), at, 0.016)

    # Air / paper texture, high-passed noise, slowly moving.
    noise = rng.standard_normal(N).astype(np.float32)
    sos = butter(2, 1400, btype="highpass", fs=SR, output="sos")
    air = sosfilt(sos, noise).astype(np.float32)
    bed += air * (0.0022 + 0.0018 * (0.5 + 0.5 * np.sin(2 * np.pi * 0.043 * t)))

    # Transition swells at every visual cut.
    cuts = [5.42, 11.13, 17.37, 20.69, 28.15, 30.68, 35.91, 44.02]
    sos_band = butter(2, [320, 3200], btype="bandpass", fs=SR, output="sos")
    for cut in cuts:
        dur = 0.72
        n = int(dur * SR)
        tt = np.arange(n) / SR
        nz = rng.standard_normal(n).astype(np.float32)
        nz = sosfilt(sos_band, nz).astype(np.float32)
        shape = np.sin(np.pi * tt / dur) ** 1.6
        add_at(bed, (nz * shape).astype(np.float32), cut - dur * 0.58, 0.018)

    # UI / paper clicks and ticks.
    def click(freq=1600.0, dur=0.045, tone=0.5, noise=0.5):
        n = int(dur * SR)
        tt = np.arange(n) / SR
        s = tone * np.sin(2 * np.pi * freq * tt) * np.exp(-tt * 90.0)
        s += noise * rng.standard_normal(n) * np.exp(-tt * 120.0)
        return s.astype(np.float32)

    add_at(bed, click(920, 0.07, 0.45, 0.55), 20.08, 0.045)   # « Un clic » (scene 4)
    add_at(bed, click(1180, 0.055, 0.42, 0.58), 36.50, 0.032)  # validation produit
    for at, f in [(36.62, 1560), (37.82, 1740), (39.10, 1860), (41.60, 1980)]:
        add_at(bed, click(f, 0.035, 0.55, 0.25), at, 0.020)

    # Signature chime, warm and short.
    n = int(2.2 * SR)
    tt = np.arange(n) / SR
    chime = (
        0.55 * np.sin(2 * np.pi * 523.25 * tt) * np.exp(-tt * 1.7)
        + 0.35 * np.sin(2 * np.pi * 659.25 * tt) * np.exp(-tt * 1.9)
        + 0.22 * np.sin(2 * np.pi * 783.99 * tt) * np.exp(-tt * 2.2)
    )
    add_at(bed, chime.astype(np.float32), 44.02, 0.034)

    # Gentle low-pass so the bed never fights the voice.
    sos_lp = butter(2, 7800, btype="lowpass", fs=SR, output="sos")
    bed = sosfilt(sos_lp, bed).astype(np.float32)
    return bed


def main():
    voice_raw = read_mono(TMP / "jilms-vo-44k.wav")
    voice_raw = fit(voice_raw, N)
    # Remove any DC and use short fades so the file never clicks at the edges.
    voice_raw -= float(np.mean(voice_raw))
    fade_in = int(0.010 * SR)
    voice_raw[:fade_in] *= np.linspace(0, 1, fade_in, endpoint=False)
    fade = int(0.020 * SR)
    voice_raw[-fade:] *= np.linspace(1, 0, fade, endpoint=True)

    voice = compressor(voice_raw, threshold_db=-23.5, ratio=2.6,
                       attack_ms=7.0, release_ms=140.0)
    # Rough makeup gain; the loop below nails the loudness.
    voice *= 1.55
    voice = peak_limit(voice, -2.2)

    meter = pyln.Meter(SR)
    target_voice_lufs = -17.4
    for _ in range(4):
        loud = meter.integrated_loudness(voice)
        voice *= 10.0 ** ((target_voice_lufs - loud) / 20.0)
        voice = peak_limit(voice, -2.0)

    bed = make_bed()
    # Keep the bed at a consistent low level under the voice.
    bed = bed / max(1e-9, np.max(np.abs(bed))) * 0.14
    # Duck the bed very slightly under the voice using a slow envelope.
    env = np.abs(voice)
    sos_env = butter(1, 3.0, btype="lowpass", fs=SR, output="sos")
    env = sosfilt(sos_env, env).astype(np.float32)
    env = env / max(1e-9, np.percentile(env, 95))
    duck = 1.0 - 0.20 * np.clip(env, 0, 1)
    bed *= duck

    mix = voice + bed
    mix = compressor(mix, threshold_db=-18.0, ratio=1.8,
                     attack_ms=12.0, release_ms=180.0)
    mix = peak_limit(mix, -1.3)
    loud = meter.integrated_loudness(mix)
    target_mix_lufs = -16.0
    mix *= 10.0 ** ((target_mix_lufs - loud) / 20.0)
    mix = peak_limit(mix, -1.3)

    # Final safety: exact 48.000 s, 44.1 kHz, 16-bit mono.
    mix = fit(mix, N)
    fade_out = int(0.30 * SR)
    mix[-fade_out:] *= np.linspace(1, 0, fade_out, endpoint=True)
    voice_out = fit(voice, N)
    sf.write(OUT / "JILMS-motion-48s-vo-mix-v5.wav", mix, SR, subtype="PCM_16")
    sf.write(OUT / "JILMS-motion-48s-vo-v5.wav", voice_out, SR, subtype="PCM_16")

    manifest = {
        "version": "V5",
        "duration_s": TOTAL,
        "sample_rate": SR,
        "channels": 1,
        "source": ".audio-tmp/jilms-vo-44k.wav (raw 47.804 s continuous take, NORMAL SPEED, no stretch)",
        "stretch_factor": 1.0,
        "scene_starts_s": [0, 5.42, 11.13, 17.37, 20.69, 28.15, 30.68, 35.91, 44.02],
        "voice_word_cues_s": {
            "pas_le_bureau": 3.46,
            "le_cahier": 5.68,
            "les_recus": 6.66,
            "les_post_it": 7.84,
            "whatsapp": 8.78,
            "les_ventes": 11.28,
            "le_stock": 12.38,
            "la_compta": 14.48,
            "et_le_soir": 17.52,
            "un_clic": 20.08,
            "et_tout_se_range": 20.90,
            "les_ventes_deviennent": 22.40,
            "le_stock_devient": 24.28,
            "la_comptabilite": 26.04,
            "une_seule_base": 28.14,
            "zero_ressaisie": 29.50,
            "conforme": 30.72,
            "mobile_money": 33.34,
            "pense": 34.34,
            "regardez": 36.08,
            "vous_validez": 36.62,
            "le_stock_maj": 37.82,
            "les_ecritures": 39.10,
            "le_tableau": 40.44,
            "c_est_ca": 41.60,
            "signature": 44.02
        },
        "click_s": [20.08, 36.50],
        "signature_chime_s": 44.02,
        "integrated_lufs": round(float(meter.integrated_loudness(mix)), 2),
        "peak_dbfs": round(float(20 * np.log10(np.max(np.abs(mix)))), 2),
        "voice_integrated_lufs": round(float(meter.integrated_loudness(voice_out)), 2),
        "voice_peak_dbfs": round(float(20 * np.log10(np.max(np.abs(voice_out)))), 2),
        "notes": "Normal-speed continuous VO (no time-stretch). Bed is a new light scratch; final music still to be produced."
    }
    (TMP / "v5-audio-manifest.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False))
    print(json.dumps(manifest, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
