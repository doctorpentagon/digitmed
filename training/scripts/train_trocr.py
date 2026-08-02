"""Portable TrOCR fine-tuning entry point for Kaggle or Colab.

Input JSONL records require `image` (path relative to --data-root) and human-verified
`text`. Run --dry-run first; do not upload raw or unredacted health data to a notebook.
"""
import argparse, json, os
from pathlib import Path

import evaluate
import torch
from PIL import Image
from torch.utils.data import Dataset
from transformers import (EarlyStoppingCallback, Seq2SeqTrainer, Seq2SeqTrainingArguments,
                          TrOCRProcessor, VisionEncoderDecoderModel, default_data_collator)

class LineDataset(Dataset):
    def __init__(self, jsonl, root, processor):
        self.rows = [json.loads(line) for line in Path(jsonl).read_text(encoding="utf-8").splitlines() if line.strip()]
        self.root, self.processor = Path(root), processor
    def __len__(self): return len(self.rows)
    def __getitem__(self, index):
        row = self.rows[index]; image = Image.open(self.root / row["image"]).convert("RGB")
        pixels = self.processor(images=image, return_tensors="pt").pixel_values.squeeze(0)
        labels = self.processor.tokenizer(row["text"], padding="max_length", max_length=128, truncation=True).input_ids
        labels = [token if token != self.processor.tokenizer.pad_token_id else -100 for token in labels]
        return {"pixel_values": pixels, "labels": torch.tensor(labels)}

def metrics(processor):
    cer, wer = evaluate.load("cer"), evaluate.load("wer")
    def calculate(result):
        predictions, labels = result.predictions, result.label_ids
        labels[labels == -100] = processor.tokenizer.pad_token_id
        prediction_text = processor.batch_decode(predictions, skip_special_tokens=True)
        label_text = processor.batch_decode(labels, skip_special_tokens=True)
        return {"cer": cer.compute(predictions=prediction_text, references=label_text), "wer": wer.compute(predictions=prediction_text, references=label_text)}
    return calculate

def main():
    parser = argparse.ArgumentParser(); parser.add_argument("--data-root", required=True); parser.add_argument("--train", required=True); parser.add_argument("--validation", required=True)
    parser.add_argument("--output", required=True); parser.add_argument("--model", default="microsoft/trocr-base-handwritten"); parser.add_argument("--epochs", type=int, default=12)
    parser.add_argument("--batch-size", type=int, default=4); parser.add_argument("--grad-accumulation", type=int, default=8); parser.add_argument("--dry-run", action="store_true"); args = parser.parse_args()
    processor = TrOCRProcessor.from_pretrained(args.model); train_set = LineDataset(args.train, args.data_root, processor); validation_set = LineDataset(args.validation, args.data_root, processor)
    if not train_set or not validation_set: raise ValueError("Train and validation JSONL must both contain verified line pairs")
    if args.dry_run: print(json.dumps({"train_examples": len(train_set), "validation_examples": len(validation_set), "first_train": train_set.rows[0]}, indent=2)); return
    model = VisionEncoderDecoderModel.from_pretrained(args.model)
    model.config.decoder_start_token_id = processor.tokenizer.cls_token_id; model.config.pad_token_id = processor.tokenizer.pad_token_id; model.config.eos_token_id = processor.tokenizer.sep_token_id
    model.config.max_length = 128; model.config.num_beams = 4; model.gradient_checkpointing_enable()
    settings = Seq2SeqTrainingArguments(output_dir=args.output, per_device_train_batch_size=args.batch_size, per_device_eval_batch_size=args.batch_size, gradient_accumulation_steps=args.grad_accumulation, learning_rate=3e-5, num_train_epochs=args.epochs, fp16=torch.cuda.is_available(), predict_with_generate=True, evaluation_strategy="steps", eval_steps=100, save_strategy="steps", save_steps=100, save_total_limit=2, load_best_model_at_end=True, metric_for_best_model="cer", greater_is_better=False, logging_steps=20, report_to="none", dataloader_num_workers=min(4, os.cpu_count() or 1), optim="adamw_torch")
    trainer = Seq2SeqTrainer(model=model, args=settings, train_dataset=train_set, eval_dataset=validation_set, data_collator=default_data_collator, compute_metrics=metrics(processor), callbacks=[EarlyStoppingCallback(early_stopping_patience=3)])
    trainer.train(); trainer.save_model(args.output); processor.save_pretrained(args.output); print(trainer.evaluate())

if __name__ == "__main__": main()
