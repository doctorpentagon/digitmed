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

```bash
pip install -q -r training/requirements-train.txt
python training/scripts/train_trocr.py --data-root /kaggle/input/digitmed-trocr-dataset --train /kaggle/input/digitmed-trocr-dataset/trocr/train.jsonl --validation /kaggle/input/digitmed-trocr-dataset/trocr/validation.jsonl --output /kaggle/working/digitmed-trocr-v1 --dry-run
```

Review the dry-run output first. Then remove `--dry-run` to train. On Colab replace `/kaggle/input/...` and `/kaggle/working/...` with the mounted Drive paths. Begin with one GPU; multi-GPU adds complexity and is unnecessary for a small verified pilot dataset.

## Do not waste GPU time

1. Run local preprocessing and JSONL validation before upload.
2. Run `--dry-run` in Kaggle/Colab.
3. Run a zero-shot TrOCR benchmark against the test split before fine-tuning.
4. Fine-tune only when there are enough verified line pairs to keep a held-out test split untouched.
5. Download `digitmed-trocr-v1/` from notebook outputs, hash/register it locally, then evaluate it on the untouched test split.
