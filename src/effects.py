import numpy as np

from scipy.signal import butter, sosfilt
from src.config import get_config

def applyEffect(pcm: np.ndarray, effect: int, sample_rate: int = 44100, vol: float = 1.0) -> np.ndarray:
    pcm = pcm.astype(np.float32)
    peak = np.max(np.abs(pcm))
    if peak > 0:
        pcm = pcm / peak
    pcm *= 0.45 * vol

    if effect == 0:
        return pcm
    if effect == 1:
        return _radio(pcm, sample_rate)
    if effect == 2:
        return _walkie(pcm, sample_rate)
    if effect == 3:
        return _phone(pcm, sample_rate)
    if effect == 4:
        return _megaphone(pcm, sample_rate)
    if effect == 5:
        return _underwater(pcm, sample_rate)
    if effect == 6:
        return _mystical(pcm, sample_rate)
    return pcm

def _bandpassFilter(data: np.ndarray, low: float, high: float, sr: int) -> np.ndarray:
    sos = butter(4, [low, high], btype="band", fs=sr, output="sos")
    return sosfilt(sos, data).astype(np.float32)

def _lowpassFilter(data: np.ndarray, cutoff: float, sr: int) -> np.ndarray:
    sos = butter(4, cutoff, btype="low", fs=sr, output="sos")
    return sosfilt(sos, data).astype(np.float32)

def _softClip(data: np.ndarray, drive: float = 1.5) -> np.ndarray:
    driven = data * drive
    return np.tanh(driven).astype(np.float32)

def _generateNoise(data: np.ndarray, amount: float = 0.02) -> np.ndarray:
    noise = np.random.default_rng(42).normal(0, amount, len(data)).astype(np.float32)
    return data + noise

def _wobble(data: np.ndarray, sr: int, amount: float = 0.15, freq: float = 2.0) -> np.ndarray:
    t = np.arange(len(data), dtype=np.float32) / (sr * 2)
    mod = 1.0 + amount * np.sin(2 * np.pi * freq * t)
    return (data * mod).astype(np.float32)

def _reverb(data: np.ndarray, sr: int, decay: float = 0.3, delay_ms: float = 40) -> np.ndarray:
    delay_samples = int(sr * delay_ms / 1000) * 2  # stereo interleaved
    out = data.copy()
    for tap in range(1, 4):
        offset = delay_samples * tap
        gain = decay ** tap
        if offset < len(out):
            out[offset:] += data[:len(data) - offset] * gain
    return out.astype(np.float32)

def _radio(pcm: np.ndarray, sr: int) -> np.ndarray:
    cfg = get_config()["effects"]["radio"]
    filtered = _bandpassFilter(pcm, cfg["band_low"], cfg["band_high"], sr)
    return _softClip(filtered, drive=cfg["drive"])

def _walkie(pcm: np.ndarray, sr: int) -> np.ndarray:
    cfg = get_config()["effects"]["walkie"]
    filtered = _bandpassFilter(pcm, cfg["band_low"], cfg["band_high"], sr)
    clipped = _softClip(filtered, drive=cfg["drive"])
    return _generateNoise(clipped, amount=cfg["noise"])

def _phone(pcm: np.ndarray, sr: int) -> np.ndarray:
    cfg = get_config()["effects"]["phone"]
    filtered = _bandpassFilter(pcm, cfg["band_low"], cfg["band_high"], sr)
    return _softClip(filtered, drive=cfg["drive"])


def _megaphone(pcm: np.ndarray, sr: int) -> np.ndarray:
    cfg = get_config()["effects"]["megaphone"]
    filtered = _bandpassFilter(pcm, cfg["band_low"], cfg["band_high"], sr)
    clipped = _softClip(filtered, drive=cfg["drive"])
    return clipped * cfg["boost"]

def _underwater(pcm: np.ndarray, sr: int) -> np.ndarray:
    cfg = get_config()["effects"]["underwater"]
    filtered = _lowpassFilter(pcm, cfg["cutoff"], sr)
    wet = _reverb(filtered, sr, decay=cfg["reverb_decay"], delay_ms=cfg["reverb_delay_ms"])
    return _wobble(wet, sr, amount=cfg["wobble_amount"], freq=cfg["wobble_freq"])

def _mystical(pcm: np.ndarray, sr: int) -> np.ndarray:
    cfg = get_config()["effects"]["mystical"]
    wet = _reverb(pcm, sr, decay=cfg["reverb_decay"], delay_ms=cfg["reverb_delay_ms"])
    shimmer = _reverb(pcm, sr, decay=cfg["shimmer_decay"], delay_ms=cfg["shimmer_delay_ms"])
    mixed = wet * cfg["dry_wet_mix"] + shimmer * (1.0 - cfg["dry_wet_mix"])
    return mixed.astype(np.float32)