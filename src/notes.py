from src.synth import NoteEvent
from src.models import TtsRequest
from src.config import get_config

SCALES = {
    0: [0, 2, 4, 7, 9],             # Major Pentatonic
    1: [0, 3, 5, 7, 10],            # Minor Pentatonic
    2: [0, 3, 5, 6, 7, 10],         # Blues
    3: list(range(12)),             # Chromatic
    4: [0, 2, 4, 5, 7, 9, 11],      # Major
    5: [0, 2, 3, 5, 7, 8, 10],      # Minor
    6: [0, 2, 3, 5, 7],             # Bass (low-register pentatonic)
}

_cfg = get_config()["notes"]

BASE_NOTE = _cfg["base_note"]
SPACE_PAUSE_BASE = _cfg["space_pause_base"]
PUNCT_PAUSE_BASE = _cfg["punct_pause_base"]


NOTE_DURATION_BASE = _cfg["note_duration_base"]
HARMONY_VELOCITY_DROPOFF = _cfg["harmony_velocity_dropoff"]

PAUSE_CHARS = {" "}
LONG_PAUSE_CHARS = {".", ",", "!", "?", "-"}

def text_to_notes(request: TtsRequest) -> list[NoteEvent]:
    scale = SCALES[request.scale]
    base_velocity = min(127, max(1, int(127 * request.vol)))

    notes: list[NoteEvent] = []

    for char in request.t:
        if char in PAUSE_CHARS:
            notes.append(NoteEvent(notes=[], duration=SPACE_PAUSE_BASE * request.pause))
            continue

        if char in LONG_PAUSE_CHARS:
            notes.append(NoteEvent(notes=[], duration=PUNCT_PAUSE_BASE * request.pause))
            continue

        if not char.isalnum():
            continue

        midi_note = convertNotes(char, scale, request.pitch)
        chord: list[tuple[int, int]] = [(midi_note, base_velocity)]

        for i in range(1, request.poly):
            harm = createHarmony(midi_note, scale, i)
            chord.append((harm, max(1, base_velocity - HARMONY_VELOCITY_DROPOFF * i)))

        notes.append(NoteEvent(notes=chord, duration=NOTE_DURATION_BASE * request.speed))

    return notes

def convertNotes(char: str, scale: list[int], pitch_offset: int) -> int:
    index = ord(char.lower()) % len(scale)
    note = BASE_NOTE + scale[index] + pitch_offset
    return max(0, min(127, note))

def createHarmony(base: int, scale: list[int], interval: int) -> int:
    closest_idx = min(range(len(scale)), key=lambda i: abs((base % 12) - scale[i]))
    harmony_idx = (closest_idx + interval * 2) % len(scale)
    octave = base // 12
    note = octave * 12 + scale[harmony_idx]
    if note <= base:
        note += 12
    return max(0, min(127, note))