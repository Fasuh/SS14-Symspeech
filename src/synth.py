import json
from pathlib import Path
from dataclasses import dataclass

import fluidsynth
import numpy as np

from src.config import get_config

@dataclass
class NoteEvent:
    notes: list[tuple[int, int]]
    duration: float

class Synthesizer:
    def __init__(self):
        cfg = get_config()["synth"]
        root = Path(__file__).parent.parent

        self.sample_rate = cfg["sample_rate"]
        self.final_release_time = cfg["final_release_time"]
        self.voices = self._load_voices(root / cfg["voices_path"])
        self.fs = fluidsynth.Synth(samplerate=float(self.sample_rate))

        soundfonts_dir = root / cfg["soundfonts_dir"]
        self.sfid: dict[str, int] = {}
        for filename in cfg["soundfonts"]:
            path = str(soundfonts_dir / filename)
            sfid = self.fs.sfload(path)
            self.sfid[filename] = sfid

    def _load_voices(self, path: Path) -> dict[str, dict]:
        with open(path) as f:
            return json.load(f)

    def render(self, voice_id: str, notes: list[NoteEvent]) -> np.ndarray:
        voice = self.voices[voice_id]
        sfid = self.sfid[voice["soundfont"]]

        self.fs.program_select(0, sfid, voice["bank"], voice["program"])

        chunks: list[np.ndarray] = []
        active_notes: list[int] = []

        for event in notes:
            if not event.notes:
                for n in active_notes:
                    self.fs.noteoff(0, n)
                active_notes.clear()

                silence_samples = int(event.duration * self.sample_rate)
                chunks.append(self.fs.get_samples(silence_samples))
                continue

            for n in active_notes:
                self.fs.noteoff(0, n)
            active_notes.clear()

            for note, velocity in event.notes:
                self.fs.noteon(0, note, velocity)
                active_notes.append(note)

            note_samples = int(event.duration * self.sample_rate)
            chunk = self.fs.get_samples(note_samples)
            chunks.append(chunk)

        if active_notes:
            for n in active_notes:
                self.fs.noteoff(0, n)
            tail = self.fs.get_samples(int(self.final_release_time * self.sample_rate))
            chunks.append(tail)

        if not chunks:
            return np.array([], dtype=np.float32)

        return np.concatenate(chunks)

    def close(self):
        self.fs.delete()