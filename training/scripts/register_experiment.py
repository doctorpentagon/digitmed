"""Create/update a local experiment registry entry. Registry files remain gitignored."""
import argparse, hashlib, json, subprocess
from datetime import datetime, timezone
from pathlib import Path

def file_hash(path):
    digest = hashlib.sha256();
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""): digest.update(chunk)
    return digest.hexdigest()

def git_commit():
    try: return subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
    except Exception: return "unknown"

def main():
    parser = argparse.ArgumentParser(); parser.add_argument("--registry", default="training/runs/registry.jsonl")
    parser.add_argument("--experiment-id", required=True); parser.add_argument("--dataset-version", required=True); parser.add_argument("--config", required=True)
    parser.add_argument("--metrics", required=True); parser.add_argument("--checkpoint"); parser.add_argument("--export"); parser.add_argument("--status", default="evaluated")
    args = parser.parse_args(); metrics = json.loads(Path(args.metrics).read_text(encoding="utf-8"))
    record = {"experiment_id": args.experiment_id, "created_at": datetime.now(timezone.utc).isoformat(), "git_commit": git_commit(), "dataset_version": args.dataset_version, "config_path": args.config, "task": "handwritten_text_recognition", "status": args.status, "metrics": metrics, "artifacts": {}, "approval": {"held_out_evaluation_complete": False, "clinical_review_complete": False, "approved_by": None}}
    if args.checkpoint: record["artifacts"]["checkpoint_sha256"] = file_hash(args.checkpoint)
    if args.export: record["artifacts"]["export_sha256"] = file_hash(args.export)
    target = Path(args.registry); target.parent.mkdir(parents=True, exist_ok=True)
    target.open("a", encoding="utf-8").write(json.dumps(record) + "\n"); print(json.dumps(record, indent=2))

if __name__ == "__main__": main()
