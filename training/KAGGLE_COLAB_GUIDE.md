# Kaggle / Colab TrOCR run guide

Use this only after local intake, redaction review, human verification, and writer/facility-safe splitting. A notebook is external processing: upload **only approved de-identified derivatives** and their verified JSONL labels.

## You do not manually download the model

The public model is fetched automatically by `TrOCRProcessor.from_pretrained("microsoft/trocr-base-handwritten")` and `VisionEncoderDecoderModel.from_pretrained(...)`. Do not look for a GGUF Q4 file.

## Prepare one dataset folder

```text
digitmed-trocr-dataset/
  processed/dm_<anonymous-id>.png
  trocr/train.jsonl
  trocr/validation.jsonl
  trocr/test.jsonl            # Do not use until training is complete.
```

Each JSONL row is exactly:

```json
{"sample_id":"dm_123","image":"processed/dm_123.png","text":"human-verified transcription","document_type":"other","source_group":"old_handwriting_split_1"}
```

## Kaggle or Colab cells

### 1. Upload only the approved package

In Kaggle, use **+ Add Input** → **Upload a dataset**. Upload the generated `digitmed-trocr-dataset/` package only: anonymous processed images plus verified JSONL/CSV metadata. Never upload the original Drive export, source-name mapping, raw clinical images, unreviewed transcripts, or redaction records.

### 2. Run this preflight cell before installing or training

```python
import json
import os
from pathlib import Path
import torch

print(f"GPU available: {torch.cuda.is_available()}")
print(f"GPU count: {torch.cuda.device_count()}")
if torch.cuda.is_available():
    print(f"GPU: {torch.cuda.get_device_name(0)}")

input_root = Path("/kaggle/input")
datasets = [path for path in input_root.iterdir() if path.is_dir()]
print("Available Kaggle datasets:", [path.name for path in datasets])

# Replace this after reading the printed dataset folder name.
dataset_root = input_root / "REPLACE_WITH_DATASET_FOLDER"
metadata = dataset_root / "trocr" / "train.jsonl"
if not metadata.exists():
    raise FileNotFoundError(f"Expected verified training metadata at {metadata}")

first_row = json.loads(metadata.read_text(encoding="utf-8").splitlines()[0])
required_columns = {"sample_id", "image", "text", "document_type", "source_group"}
missing = required_columns - set(first_row)
if missing:
    raise ValueError(f"Training JSONL is missing columns: {sorted(missing)}")
print("Verified metadata columns:", sorted(first_row))
print("Preflight passed. Review this output before continuing.")
```

Record the exact Kaggle folder name and the printed metadata columns in the experiment registry. The standard DigitMed training format is JSONL—not CSV—but a CSV can be converted locally before upload if it has at least `file_name`/`image` and `text` columns.

### 3. Validate without consuming training time

```bash
pip install -q -r training/requirements-train.txt
python training/scripts/train_trocr.py --data-root /kaggle/input/digitmed-trocr-dataset --train /kaggle/input/digitmed-trocr-dataset/trocr/train.jsonl --validation /kaggle/input/digitmed-trocr-dataset/trocr/validation.jsonl --output /kaggle/working/digitmed-trocr-v1 --dry-run
```

Review the preflight and dry-run output first. Then remove `--dry-run` to train. On Colab replace `/kaggle/input/...` and `/kaggle/working/...` with the mounted Drive paths. Begin with one GPU; multi-GPU adds complexity and is unnecessary for a small verified pilot dataset.

## Do not waste GPU time

1. Run local preprocessing and JSONL validation before upload.
2. Run `--dry-run` in Kaggle/Colab.
3. Run a zero-shot TrOCR benchmark against the test split before fine-tuning.
4. Fine-tune only when there are enough verified line pairs to keep a held-out test split untouched.
5. Download `digitmed-trocr-v1/` from notebook outputs, hash/register it locally, then evaluate it on the untouched test split.
