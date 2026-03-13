import io
import numpy as np
import soundfile as sf

def pcm_to_ogg(pcm: np.ndarray, sample_rate: int = 44100) -> bytes:
    stereo = pcm.reshape(-1, 2)

    buf = io.BytesIO()
    sf.write(buf, stereo, sample_rate, format="OGG", subtype="VORBIS")
    return buf.getvalue()