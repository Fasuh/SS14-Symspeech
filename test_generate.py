import json
import sys
from pathlib import Path

from src.generate import generate
from src.models import TtsRequest


def main():
    input_path = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("test/test_requests.json")
    output_dir = Path(sys.argv[2]) if len(sys.argv) > 2 else Path("test/output")

    output_dir.mkdir(parents=True, exist_ok=True)

    with open(input_path) as f:
        requests = json.load(f)

    for i, raw in enumerate(requests):
        request = TtsRequest(**raw)
        print(f"  [{i + 1}/{len(requests)}] {request.id} — \"{request.t[:40]}...\" voice={request.r}")

        ogg = generate(request)

        out_path = output_dir / f"{request.id}.ogg"
        out_path.write_bytes(ogg)
        print(f"           -> {out_path} ({len(ogg)} bytes)")

    print("Done.")


if __name__ == "__main__":
    main()