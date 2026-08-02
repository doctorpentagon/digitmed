"""Creates a deliberately imperfect local prediction fixture to validate evaluation plumbing.

It is not OCR, has no clinical intelligence, and must never be presented as a model.
"""
import argparse, json
from pathlib import Path

def main():
    parser = argparse.ArgumentParser(); parser.add_argument("--labels", required=True); parser.add_argument("--output", required=True); args = parser.parse_args()
    output = []
    for line in Path(args.labels).read_text(encoding="utf-8").splitlines():
        if not line.strip(): continue
        label = json.loads(line); fields = [{"label": field["label"], "value": field["value"], "confidence": .82} for field in label.get("fields", [])]
        output.append({"sample_id": label["sample_id"], "transcription": label["transcription"], "fields": fields})
    Path(args.output).parent.mkdir(parents=True, exist_ok=True); Path(args.output).write_text("\n".join(json.dumps(item) for item in output) + "\n", encoding="utf-8")

if __name__ == "__main__": main()
