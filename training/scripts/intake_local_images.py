"""Create de-identified local working copies from an approved image directory.

Keep the raw source directory outside Git. Original filename mapping is written only
to a gitignored restricted folder for authorised local traceability.
"""
import argparse, hashlib, json, shutil, uuid
from datetime import datetime, timezone
from pathlib import Path

ALLOWED = {".png", ".jpg", ".jpeg", ".webp"}

def sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""): digest.update(chunk)
    return digest.hexdigest()

def main():
    parser = argparse.ArgumentParser(); parser.add_argument("--source-dir", required=True); parser.add_argument("--data-root", default="training/data")
    parser.add_argument("--source-group", required=True); parser.add_argument("--limit", type=int, default=10); args = parser.parse_args()
    root = Path(args.data_root); images = root / "images"; restricted = root / "restricted"; images.mkdir(parents=True, exist_ok=True); restricted.mkdir(parents=True, exist_ok=True)
    manifest, name_map = [], []
    for source in sorted(Path(args.source_dir).iterdir()):
        if len(manifest) >= args.limit: break
        if not source.is_file() or source.suffix.lower() not in ALLOWED: continue
        sample_id = f"dm_{uuid.uuid4().hex[:16]}"; extension = source.suffix.lower(); destination = images / f"{sample_id}{extension}"; shutil.copy2(source, destination)
        manifest.append({"sample_id": sample_id, "working_image_path": f"images/{destination.name}", "facility_id": "pending_assignment", "writer_id": None, "source_group": args.source_group, "document_type": "other", "consent_status": "not_approved", "deidentified_at": datetime.now(timezone.utc).isoformat(), "redaction_reviewed": False, "annotation_status": "unassigned", "capture_quality": "other"})
        name_map.append({"sample_id": sample_id, "original_filename": source.name, "source_sha256": sha256(source)})
    (root / "manifest-draft.jsonl").write_text("\n".join(json.dumps(item) for item in manifest) + "\n", encoding="utf-8")
    (restricted / "source-name-map.jsonl").write_text("\n".join(json.dumps(item) for item in name_map) + "\n", encoding="utf-8")
    print(json.dumps({"working_copies": len(manifest), "manifest": str(root / "manifest-draft.jsonl"), "restricted_mapping": str(restricted / "source-name-map.jsonl"), "next_step": "human redaction and consent review required"}, indent=2))

if __name__ == "__main__": main()
