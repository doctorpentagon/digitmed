"""Create deterministic facility/writer-grouped train, validation and test splits."""
import argparse, hashlib, json
from collections import defaultdict
from pathlib import Path

def split_for(group, seed):
    value = int(hashlib.sha256(f"{seed}:{group}".encode()).hexdigest()[:8], 16) % 100
    return "train" if value < 70 else "validation" if value < 85 else "test"

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--seed", default="42")
    args = parser.parse_args()
    rows = [json.loads(line) for line in Path(args.manifest).read_text(encoding="utf-8").splitlines() if line.strip()]
    groups, facility_splits = defaultdict(list), defaultdict(set)
    for row in rows:
        if row.get("consent_status") != "approved" or not row.get("redaction_reviewed"):
            raise ValueError(f"{row.get('sample_id')}: consent/redaction gate not satisfied")
        group = row.get("writer_id") or f"facility:{row['facility_id']}"
        row["split"] = split_for(group, args.seed); groups[group].append(row); facility_splits[row["facility_id"]].add(row["split"])
    Path(args.output).write_text("\n".join(json.dumps(row, ensure_ascii=False) for rows in groups.values() for row in rows) + "\n", encoding="utf-8")
    print(json.dumps({"samples": len(rows), "groups": len(groups), "facility_split_distribution": {key: sorted(value) for key, value in facility_splits.items()}}, indent=2))

if __name__ == "__main__": main()
