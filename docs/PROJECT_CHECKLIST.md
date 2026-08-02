# DigitMed Delivery Checklist

This is the working source of truth for delivery. It is updated as work is completed. A checked item is implemented and verified; an unchecked item is planned, awaiting a decision, or blocked by an external dependency.

## 1. Foundation and GitHub readiness

- [x] Review the V1 build specification, supplied screen exports, research plan, competitive analysis, pitch, and coding standards.
- [x] Correct the project name to **DigitMed**.
- [x] Build the React/Vite frontend foundation and Flask API contract stub.
- [x] Establish the design tokens: Poppins, Inter, green product controls, orange marketing CTAs, responsive breakpoints, and accessibility motion preference.
- [x] Create a deployable Vercel configuration and Render API configuration.
- [x] Initialise a local Git repository.
- [x] Write the core deployment README.
- [x] Resolve the Windows Git safe-directory warning.
- [ ] Create or connect the GitHub repository.
- [x] Make the first clean, reviewed commit (`d66772d`).

## 2. Pilot product completion

- [x] Public landing, hospital, pricing, developer, sign-up, and log-in views.
- [x] Use the supplied handwritten clinical-note image in the landing conversion demo.
- [x] Dashboard, upload source selection, type confirmation, staged conversion, review, structured record, failure, history, batch, service, settings, and status views.
- [x] Local mock conversion with realistic progress, confidence, and intentional failure conditions.
- [x] IndexedDB source-file preservation before conversion.
- [x] Field-level confidence handling and source provenance highlight.
- [x] Client-side FHIR Bundle generation and download.
- [x] Product copy for Nigerian hospitals, clinics, and health builders.
- [ ] Camera capture, crop, and blur-quality assessment flow.
- [ ] Full-screen provenance lightbox and record PDF export.
- [ ] Batch error triage and all remaining detailed modal states from the build specification.
- [ ] Browser/device visual QA at 390px, tablet, and desktop reference widths.
- [ ] Automated component, state-machine, and accessibility tests.

## 3. Supabase backend and future identity

- [x] Select Supabase as the persistent backend direction.
- [ ] Create a Supabase project in the correct data-residency region.
- [ ] Add database migrations for facilities, users, documents, conversion jobs, records, field provenance, audit events, and subscriptions.
- [ ] Add private Storage buckets with signed upload/download URLs.
- [ ] Add Row Level Security policies before real facility data is stored.
- [ ] Add Edge Functions or a secure API boundary for conversion-job creation.
- [ ] Connect the frontend to Supabase in demo-safe mode.
- [ ] Add Google OAuth and email/password sign-in when explicitly enabled.
- [ ] Add role-based access: clinician, facility administrator, service operator, developer.

## 4. V1 clinical document intelligence harness

- [x] Define the model boundary: image quality → classification → handwriting recognition → clinical structuring → confidence/provenance → human review.
- [ ] Create a consented-data manifest and de-identification workflow.
- [ ] Define annotation schemas for transcription, document type, field extraction, polygons/bounding boxes, and review status.
- [ ] Build image preprocessing: rotation, crop, illumination, blur detection, redaction, and quality reports.
- [ ] Create reproducible train/validation/test splits by facility and writer, preventing data leakage.
- [ ] Implement baseline OCR/model benchmark adapters.
- [ ] Implement metric reporting: CER, WER, field accuracy, confidence calibration, and review workload.
- [ ] Add a training configuration for a GPU environment.
- [ ] Add model registry metadata, experiment records, and reproducible model export.
- [ ] Evaluate held-out Nigerian clinical handwriting before any public accuracy claim.

## 5. Real model and conversion service

- [ ] Select a baseline model after the benchmark, not before it.
- [ ] Provision approved GPU compute and secure training storage.
- [ ] Train/fine-tune V1 only on consented, de-identified data.
- [ ] Deploy an asynchronous conversion worker with queue, retries, timeouts, and retained-source guarantee.
- [ ] Add human review queue and correction feedback loop.
- [ ] Perform facility pilot acceptance testing.
- [ ] Decide whether an offline GGUF/llama.cpp component is justified for the chosen model architecture.

## 6. Production readiness and release

- [ ] Approve consent language, data-processing agreement, retention policy, and incident path.
- [ ] Complete a Nigeria Data Protection Act 2023 / GAID 2025 review with a qualified professional.
- [ ] Add monitoring, error reporting, backups, and audit logging.
- [ ] Run security, accessibility, performance, and failure-mode tests.
- [ ] Deploy frontend to Vercel and API/workers to Render or approved infrastructure.
- [ ] Configure the production domain, environment variables, and status page.
- [ ] Create a versioned downloadable release archive.
- [ ] Run final pilot handoff and document operations.

## Decisions recorded

| Topic | Decision | Status |
|---|---|---|
| Product name | DigitMed | Confirmed |
| V1 access | Direct, demo-safe access; no enforced authentication | Confirmed |
| Future backend | Supabase | Confirmed |
| Future sign-in | Google OAuth and email/password via Supabase Auth | Deferred |
| V1 AI mode | Local realistic mock adapter | Confirmed |
| Training environment | Portable GPU harness, then approved cloud GPU | Planned |
| Current local GPU | Quadro M1000M, 2 GB VRAM | Insufficient for meaningful training |
