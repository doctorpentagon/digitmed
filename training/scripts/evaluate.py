"""Model-neutral DigitMed benchmark metrics for held-out clinical handwriting labels.

Prediction records are JSONL: sample_id, transcription, fields [{label,value,confidence}].
This script deliberately makes no network calls and does not select a model.
"""
import argparse, json, math
from collections import defaultdict
from pathlib import Path

def rows(path):
    return {row["sample_id"]: row for row in (json.loads(line) for line in Path(path).read_text(encoding="utf-8").splitlines() if line.strip())}

def distance(reference, hypothesis):
    previous = list(range(len(hypothesis) + 1))
    for i, left in enumerate(reference, 1):
        current = [i]
        for j, right in enumerate(hypothesis, 1): current.append(min(current[-1] + 1, previous[j] + 1, previous[j - 1] + (left != right)))
        previous = current
    return previous[-1]

def words(value): return value.lower().split()
def normalise(value): return " ".join(value.lower().split())

def main():
    parser = argparse.ArgumentParser(); parser.add_argument("--labels", required=True); parser.add_argument("--predictions", required=True)
    parser.add_argument("--output", required=True); parser.add_argument("--confidence-threshold", type=float, default=.9); args = parser.parse_args()
    labels, predictions = rows(args.labels), rows(args.predictions); characters = errors = word_errors = word_total = field_total = field_correct = review_required = 0; calibration = []
    for sample_id, label in labels.items():
        prediction = predictions.get(sample_id)
        if not prediction: continue
        reference, hypothesis = label["transcription"], prediction.get("transcription", "")
        characters += max(1, len(reference)); errors += distance(reference, hypothesis)
        reference_words, hypothesis_words = words(reference), words(hypothesis); word_total += max(1, len(reference_words)); word_errors += distance(reference_words, hypothesis_words)
        expected = {normalise(item["label"]): normalise(item["value"]) for item in label.get("fields", [])}; actual = {normalise(item["label"]): item for item in prediction.get("fields", [])}
        for name, value in expected.items():
            item = actual.get(name); correct = bool(item and normalise(item.get("value", "")) == value); field_total += 1; field_correct += correct
            confidence = float(item.get("confidence", 0)) if item else 0; calibration.append((confidence, int(correct)))
            if confidence < args.confidence_threshold: review_required += 1
    brier = sum((confidence - correct) ** 2 for confidence, correct in calibration) / max(1, len(calibration))
    report = {"samples_evaluated": len([key for key in labels if key in predictions]), "cer": round(errors / max(1, characters), 4), "wer": round(word_errors / max(1, word_total), 4), "field_accuracy": round(field_correct / max(1, field_total), 4), "confidence_brier_score": round(brier, 4), "reviewer_workload": {"fields_below_threshold": review_required, "rate": round(review_required / max(1, field_total), 4)}, "notes": ["CER/WER lower is better.", "Brier score lower is better.", "Metrics are valid only on consented, de-identified, held-out labels."]}
    Path(args.output).parent.mkdir(parents=True, exist_ok=True); Path(args.output).write_text(json.dumps(report, indent=2), encoding="utf-8"); print(json.dumps(report, indent=2))

if __name__ == "__main__": main()
