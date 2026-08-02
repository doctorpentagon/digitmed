# DigitMed clinical-document intelligence harness

This folder is the reproducible bridge between a consented, de-identified dataset and a future handwriting-recognition model. It contains no patient data, no weights, and no claim that DigitMed has trained a clinical AI.

## Safety gate before any data enters `training/data/`

1. Obtain facility approval and a documented lawful basis/consent decision.
2. Register each item in the manifest without putting patient identifiers in the manifest.
3. Make a de-identified working derivative; retain originals only in approved, access-controlled storage.
4. Have a qualified reviewer confirm redaction before annotation or external GPU use.
5. Split by facility and writer where known before model selection or training.

`training/data/`, `training/runs/`, and `training/models/` are gitignored by design.

## Layout

```text
training/
  configs/baseline.yaml       reproducible GPU run settings
  schemas/manifest.schema.json dataset governance contract
  schemas/annotation.schema.json transcription/provenance contract
  scripts/split_dataset.py    leakage-resistant split generator
  data/                       local-only de-identified working data
  runs/                       local-only metrics and experiment outputs
  models/                     local-only model checkpoints/exports
```

## Dataset manifest

Create one JSON record per working image matching `schemas/manifest.schema.json`. `sample_id` must be random and stable. Do not store names, hospital numbers, phone numbers, addresses, dates of birth, NINs, or raw free-text clinical content in the manifest. `writer_id` is a pseudonymous writer key only; it protects the held-out evaluation split from handwriting leakage.

## Annotation standard

Each reviewed label follows `schemas/annotation.schema.json`: verified transcription, document type, structured fields, source polygons, and review outcome. Annotators must mark uncertainty rather than guessing. Clinical interpretation is out of scope; they transcribe what is present.

## Splits

Run the split script only after manifest review:

```bash
python training/scripts/split_dataset.py --manifest training/data/manifest.jsonl --output training/data/splits.jsonl
```

It keeps all examples from a known writer and facility in a single split. Hold the test split untouched until baseline selection is complete. Review the generated leakage report before training.

## GPU handoff

Use Python 3.11+, a CUDA-capable approved environment, and a private artifact store. Copy this `training/` folder plus de-identified `data/` through an approved transfer route. Start with the configuration in `configs/baseline.yaml`; record dataset version, git commit, environment, metrics, and reviewer workload for every run. Do not use the local 2 GB GPU for fine-tuning.
