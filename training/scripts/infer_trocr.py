"""Generate draft transcripts with TrOCR. Drafts require human verification."""
import argparse, json
from pathlib import Path

import torch
from PIL import Image
from transformers import TrOCRProcessor, VisionEncoderDecoderModel

def main():
    parser = argparse.ArgumentParser(); parser.add_argument("--input-dir", required=True); parser.add_argument("--output", required=True)
    parser.add_argument("--model", default="microsoft/trocr-base-handwritten"); parser.add_argument("--device", default="cuda" if torch.cuda.is_available() else "cpu")
    args = parser.parse_args(); processor = TrOCRProcessor.from_pretrained(args.model); model = VisionEncoderDecoderModel.from_pretrained(args.model).to(args.device).eval(); drafts = []
    for path in sorted(Path(args.input_dir).glob("*")):
        if path.suffix.lower() not in {".png", ".jpg", ".jpeg", ".webp"}: continue
        image = Image.open(path).convert("RGB"); pixels = processor(images=image, return_tensors="pt").pixel_values.to(args.device)
        with torch.inference_mode(): ids = model.generate(pixels, max_new_tokens=128)
        drafts.append({"image": str(path), "transcription_draft": processor.batch_decode(ids, skip_special_tokens=True)[0], "review_status": "needs_human_verification", "model": args.model})
    Path(args.output).parent.mkdir(parents=True, exist_ok=True); Path(args.output).write_text("\n".join(json.dumps(row, ensure_ascii=False) for row in drafts) + "\n", encoding="utf-8")

if __name__ == "__main__": main()
