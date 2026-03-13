from src.models import TtsRequest
from src.notes import text_to_notes
from src.synth import Synthesizer
from src.encoder import pcm_to_ogg
from src.effects import applyEffect

_synth: Synthesizer | None = None


def getSynth() -> Synthesizer:
    global _synth
    if _synth is None:
        _synth = Synthesizer()
    return _synth

def generate(request: TtsRequest) -> bytes:
    synth = getSynth()
    notes = text_to_notes(request)
    pcm = synth.render(request.r, notes)
    pcm = applyEffect(pcm, request.e, synth.sample_rate, request.vol)
    ogg = pcm_to_ogg(pcm, synth.sample_rate)
    return ogg