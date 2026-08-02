"""DigitMed's deterministic, reviewable image preprocessing pipeline.

Input images must already be consented and de-identified. Redactions are applied only
from a human-approved manifest. A missing approval fails closed by default.
"""
import argparse, json
from datetime import datetime, timezone
from pathlib import Path

import cv2
import numpy as np

def load_jsonl(path):
    return {item["sample_id"]: item for item in (json.loads(line) for line in Path(path).read_text(encoding="utf-8").splitlines() if line.strip())}

def deskew(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    points = np.column_stack(np.where(gray < 180))
    if len(points) < 30: return image, 0.0
    angle = cv2.minAreaRect(points[:, ::-1])[2]
    angle = -(90 + angle) if angle < -45 else -angle
    matrix = cv2.getRotationMatrix2D((image.shape[1] / 2, image.shape[0] / 2), angle, 1)
    return cv2.warpAffine(image, matrix, (image.shape[1], image.shape[0]), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE), round(float(angle), 2)

def normalize_illumination(image):
    lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
    lightness, a, b = cv2.split(lab)
    return cv2.cvtColor(cv2.merge((cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8)).apply(lightness), a, b)), cv2.COLOR_LAB2BGR)

def apply_redactions(image, record):
    for region in record.get("regions", []):
        x, y, width, height = (region[key] for key in ("x", "y", "width", "height"))
        image[y:y + height, x:x + width] = 0
    return image

def quality_report(image, minimum_blur):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blur = float(cv2.Laplacian(gray, cv2.CV_64F).var())
    height, width = image.shape[:2]
    flags = []
    if blur < minimum_blur: flags.append("blurred")
    if width < 640 or height < 480: flags.append("low_resolution")
    return {"width": width, "height": height, "laplacian_variance": round(blur, 2), "flags": flags, "ready_for_annotation": not flags}

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", required=True); parser.add_argument("--image-root", required=True)
    parser.add_argument("--redactions", required=True); parser.add_argument("--output-root", required=True)
    parser.add_argument("--report", required=True); parser.add_argument("--minimum-blur", type=float, default=55)
    args = parser.parse_args(); manifest = load_jsonl(args.manifest); redactions = load_jsonl(args.redactions)
    output_root = Path(args.output_root); output_root.mkdir(parents=True, exist_ok=True); report = []
    for sample_id, item in manifest.items():
        approval = redactions.get(sample_id)
        if item.get("consent_status") != "approved" or not item.get("redaction_reviewed") or not approval or not approval.get("approved_for_training"):
            report.append({"sample_id": sample_id, "status": "blocked", "reason": "consent_or_human_redaction_approval_missing"}); continue
        image = cv2.imread(str(Path(args.image_root) / item["working_image_path"]))
        if image is None: report.append({"sample_id": sample_id, "status": "blocked", "reason": "image_unreadable"}); continue
        image, angle = deskew(image); image = normalize_illumination(image); image = apply_redactions(image, approval)
        destination = output_root / f"{sample_id}.png"; cv2.imwrite(str(destination), image)
        report.append({"sample_id": sample_id, "status": "processed", "rotation_degrees": angle, "output": str(destination), **quality_report(image, args.minimum_blur)})
    Path(args.report).write_text(json.dumps({"generated_at": datetime.now(timezone.utc).isoformat(), "items": report}, indent=2), encoding="utf-8")

if __name__ == "__main__": main()
