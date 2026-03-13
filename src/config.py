import json
import os
from pathlib import Path

CONFIG_PATH = Path(__file__).parent.parent / "config.json"

_config: dict | None = None

ENV_OVERRIDES: dict[str, tuple[str, type]] = {
    "TTS_SAMPLE_RATE":              ("synth.sample_rate", int),
    "TTS_SOUNDFONTS_DIR":           ("synth.soundfonts_dir", str),
    "TTS_VOICES_PATH":              ("synth.voices_path", str),
    "TTS_FINAL_RELEASE_TIME":       ("synth.final_release_time", float),
    "TTS_BASE_NOTE":                ("notes.base_note", int),
    "TTS_SPACE_PAUSE_BASE":         ("notes.space_pause_base", float),
    "TTS_PUNCT_PAUSE_BASE":         ("notes.punct_pause_base", float),
    "TTS_NOTE_DURATION_BASE":       ("notes.note_duration_base", float),
    "TTS_HARMONY_VELOCITY_DROPOFF": ("notes.harmony_velocity_dropoff", int),
    "TTS_MAX_TEXT_LENGTH":          ("max_text_length", int),
    "TTS_REDIS_HOST":               ("redis.host", str),
    "TTS_REDIS_PORT":               ("redis.port", int),
    "TTS_REDIS_DB":                 ("redis.db", int),
    "TTS_REDIS_QUEUE":              ("redis.queue", str),
}

def _set_nested(cfg: dict, path: str, value):
    keys = path.split(".")
    for key in keys[:-1]:
        cfg = cfg[key]
    cfg[keys[-1]] = value

def _apply_env_overrides(cfg: dict):
    for env_var, (path, converter) in ENV_OVERRIDES.items():
        value = os.environ.get(env_var)
        if value is not None:
            _set_nested(cfg, path, converter(value))

def get_config() -> dict:
    global _config
    if _config is None:
        with open(CONFIG_PATH) as f:
            _config = json.load(f)
        _apply_env_overrides(_config)
    return _config