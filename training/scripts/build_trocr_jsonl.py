"""Build Hugging Face-friendly line-level JSONL from reviewed DigitMed labels.

Generated drafts may be retained separately, but only `review_status=verified`
transcripts are eligible for fine-tuning.
"""
import argparse, json
from pathlib import Path

def read_jsonl(path):
    return [json.loads(line) for line in Path(path).read_text(encoding="utf-8").splitlines() if line.strip()]

def main():
    parser = argparse.ArgumentParser(); parser.add_argument("--manifest", required=True); parser.add_argument("--annotations", required=True); parser.add_argument("--output-dir", required=True)
    args = parser.parse_args(); manifest = {item["sample_id"]: item for item in read_jsonl(args.manifest)}; annotations = read_jsonl(args.annotations)
    buckets = {"train": [], "validation": [], "test": []}; skipped = []
    for annotation in annotations:
        item = manifest.get(annotation["sample_id"])
        if not item or item.get("split") not in buckets or item.get("annotation_status") != "reviewed" or annotation.get("review_status") != "verified":
            skipped.append(annotation["sample_id"]); continue
        buckets[item["split"]].append({"sample_id": item["sample_id"], "image": f"processed/{item['sample_id']}.png", "text": annotation["transcription"], "document_type": annotation["document_type"], "source_group": item.get("source_group", "unspecified")})
    target = Path(args.output_dir); target.mkdir(parents=True, exist_ok=True)
    for split, records in buckets.items(): (target / f"{split}.jsonl").write_text("\n".join(json.dumps(record, ensure_ascii=False) for record in records) + ("\n" if records else ""), encoding="utf-8")
    print(json.dumps({"written": {split: len(records) for split, records in buckets.items()}, "skipped_unverified": len(skipped)}, indent=2))

if __name__ == "__main__": main()
