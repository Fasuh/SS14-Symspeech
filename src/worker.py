import json
import logging
import redis

from src.config import get_config
from src.models import TtsRequest
from src.generate import generate

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger("tts-worker")

def makeChannel(job_id: str, effect: int) -> str:
    if effect != 0:
        return f"result:{job_id}:{effect}"
    return f"result:{job_id}"

def publish(r: redis.Redis, channel: str, ogg: bytes):
    message = bytes([0]) + ogg
    r.publish(channel, message)
    r.publish(channel, b"__END__")

def run():
    cfg = get_config()["redis"]
    r = redis.Redis(host=cfg["host"], port=cfg["port"], db=cfg["db"])
    queue = cfg["queue"]

    r.ping()
    log.info("Connected to Redis at %s:%s", cfg["host"], cfg["port"])
    log.info("Listening on queue '%s'", queue)

    while True:
        _, raw = r.brpop(queue)

        try:
            data = json.loads(raw)
            request = TtsRequest(**data)
        except Exception as e:
            log.error("Invalid job: %s — %s", raw[:100], e)
            continue

        text_len = len(request.t)
        log.info(
            "Job %s | voice=%s pitch=%d speed=%.2f pause=%.2f poly=%d scale=%d vol=%.1f emotion=%d effect=%d | text=%d chars",
            request.id, request.r, request.pitch, request.speed, request.pause,
            request.poly, request.scale, request.vol, request.emotion, request.e, text_len
        )

        try:
            ogg = generate(request)
        except Exception as e:
            log.error("Job %s FAILED: %s", request.id, e)
            channel = makeChannel(request.id, request.e)
            r.publish(channel, b"__END__")
            continue

        channel = makeChannel(request.id, request.e)
        publish(r, channel, ogg)
        log.info("Job %s DONE | %d bytes -> %s", request.id, len(ogg), channel)

if __name__ == "__main__":
    run()