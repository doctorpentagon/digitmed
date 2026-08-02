# DigitMed

DigitMed is an Africa-first clinical-document intelligence product. It lets hospitals, clinics, clinicians, and healthcare builders move from handwritten clinical paper to structured, reviewable digital records without demanding that clinicians first abandon the writing workflow they already use.

The product begins with Nigerian clinical handwriting. The longer-term goal is trusted African health information that can support care continuity, analytics, research, quality improvement, and better locally grounded health knowledge. Every digitised record must remain reviewable against the original document.

> **Current truth:** this repository is a deployable pilot. It has no real model, no enforced authentication, no payment processing, and must not receive identifiable patient data until the required consent, privacy, security, and facility controls are operating.

## Delivery status

The authoritative checklist is [docs/PROJECT_CHECKLIST.md](docs/PROJECT_CHECKLIST.md). Work is divided into six numbered stages, with every completed item checked and every external dependency visible.

## Product scope

### What the pilot demonstrates now

- Mobile-first public site for Nigerian hospitals, clinics, and healthcare builders.
- Dashboard and direct demo-safe app access. V1 intentionally has no route guards.
- Source upload, document-type selection, realistic staged conversion, review-required state, friendly failure state, and manual-record escape path.
- Local source preservation with IndexedDB before conversion begins.
- Per-field confidence treatment, source provenance highlight, and record editing.
- Client-side FHIR Bundle generation/download.
- Pricing direction: Free pilot access with three conversions/month, Pro at ₦5,000/month, and a Hospital & API option for facility, annual, service, and builder needs.
- A quiet DigitMed Intelligence roadmap for clinical speech, text structuring, visualisation, monitoring, imaging, pathology, and child delivery.

### What the pilot deliberately does not claim

- A trained handwriting-recognition model or production clinical accuracy.
- Live OCR, healthcare decision support, diagnostic advice, or automated care decisions.
- Real authentication, authorisation, subscriptions, card billing, or patient messaging.
- Regulatory certification or production data-protection compliance.

## Design direction

The provided V1 build specification and screen exports remain the local visual authority. They are intentionally excluded from the application repository by default because they are internal project source material. The visual system follows these rules.

| Concern | Direction |
|---|---|
| Display font | Poppins, 600/700 |
| UI/body font | Inter, 400/500/600 |
| Developer code font | JetBrains Mono |
| Product primary | `#0B6E4F` green |
| Marketing primary | `#E4572E` orange |
| Page canvas | `#F4F6F5` |
| Card surface | `#FFFFFF` |
| Border | `#E3E8E6` |
| Desktop app shell | 232px green sidebar |
| Mobile app shell | fixed bottom tab bar |
| Breakpoints | 480px, 768px, 1024px, 1280px |
| Accessibility | keyboard controls, focus states, reduced-motion support, text alternatives |

Orange is used for public marketing actions. Green is used for actions inside the product. Do not reverse that rule.

## Repository structure

```text
Clinical Digitization/
├── src/
│   ├── app/                 # Routes, pages, and product composition
│   ├── lib/                 # Fixtures and shared utilities
│   ├── services/            # AI client boundary and client persistence
│   ├── styles/              # Tokens and global responsive styles
│   └── types/               # Domain models
├── public/images/           # Static project assets, including sample clinical note
├── backend/
│   ├── src/                 # Node/Express API, config, fixtures, Supabase client
│   ├── package.json
│   └── render.yaml
├── supabase/migrations/     # Postgres schema migrations, applied only after RLS review
├── docs/
│   └── PROJECT_CHECKLIST.md # Numbered build/release checklist
├── AWIBI_DIGITMED_V1_BUILD_SPEC.md
├── package.json
├── vercel.json
└── README.md
```

## Technology stack

| Layer | Technology | Why it is here |
|---|---|---|
| Frontend | React, TypeScript, Vite | Fast, typed, deployable single-page application |
| Routing | React Router | Directly addressable pilot routes without V1 auth guards |
| Icons | Lucide React | Consistent accessible SVG icon system |
| Client persistence | IndexedDB + localStorage | Preserve sources and demo jobs across reloads |
| Current API | Node.js, Express, CORS | Small clear API boundary that can be run on Render |
| Database/auth/storage | Supabase | Postgres, private Storage, future Auth, Row Level Security, and realtime options |
| Frontend hosting | Vercel | Static frontend deployment |
| API hosting | Render | Node.js web-service deployment |
| Training environment | Python + GPU environment, to be added | Reproducible preprocessing, training, and evaluation |

## Application routes

Public routes include `/`, `/for-hospitals`, `/pricing`, `/developers`, `/signup`, and `/login`.

Product routes include `/dashboard`, `/upload`, `/upload/camera`, `/upload/type`, `/convert/:jobId`, `/convert/:jobId/review`, `/convert/:jobId/failed`, `/records/:id`, `/history`, `/batch`, `/hospital-service`, `/settings`, and `/status`.

V1 routes are intentionally direct. The sign-up and log-in screens are visual demo entry points, not real identity systems.

## Beginner developer guide: how the app works

This section is deliberately practical. A new developer should read it before editing the product.

### Start here

1. Read this README and `docs/PROJECT_CHECKLIST.md` first.
2. Run the frontend locally with `npm install` then `npm run dev`.
3. Open `/upload` and follow one successful conversion from start to finish.
4. Read `src/app/App.tsx`. It currently composes the routes and the major pilot screens in one place.
5. Read `src/services/aiClient.ts`. This is the only browser-side location allowed to call the conversion API.
6. Read `backend/src/app.js`. This is the Node/Express HTTP API boundary.
7. Read `supabase/migrations/0001_digitmed_core.sql` before changing the database schema.

### Upload and conversion flow

```text
/upload
  → user selects a source file or opens /upload/camera
  → persistSource() saves the source in IndexedDB
  → React state retains the File object
  → /upload/type confirms document type
  → /convert/:jobId runs mock or live conversion
  → /convert/:jobId/review confirms low-confidence fields
  → /records/:id shows the structured, provenance-linked record
```

The key rule is that the source file must never be lost. `persistSource()` in `src/services/jobStore.ts` writes the source into IndexedDB before conversion. Do not replace in-app React Router navigation with `window.location.assign()`: a full-page reload clears the in-memory `File` object and breaks the flow.

### Camera capture

`/upload/camera` uses the browser `MediaDevices.getUserMedia()` API. Its implementation is in `CameraPage` inside `src/app/App.tsx`.

- On success, it opens the rear camera where available and converts a captured frame to a JPEG `File`.
- On permission denial, it explains the problem and offers an upload fallback.
- On unsupported devices, it offers the same upload fallback.
- The camera stream is stopped when the user leaves the screen, preventing the device camera from remaining active.

Camera permissions are requested only after the user explicitly selects **Take a photo**. Do not request camera access on page load.

### Capture review and image-quality signal

Whether a team member uploads a file or captures a photo, DigitMed routes through `/upload/review` before document type selection. `CaptureReview` creates a local preview and estimates sharpness in the browser using a downscaled canvas and Laplacian-variance calculation. It gives one of two non-blocking signals: the image looks clear enough, or it may be blurred. The reviewer can always continue, because automated image quality is a prompt for human judgement, not a clinical decision.

The assessment runs entirely on the device and does not upload image pixels. The current threshold (`variance > 55`) is a practical pilot heuristic, not a validated clinical-quality model. A manual crop/edge-correction tool is still on the roadmap; keep that distinction clear in product claims.

### Responsive quality checks

Before a frontend checkpoint is released, run `npm run build`, then inspect the core routes at 390px, 768px, and 1440px. The baseline check completed on the upload flow, tablet landing page, and desktop dashboard with no horizontal overflow. Repeat the same checks whenever a screen gains a new dense layout, table, modal, or long clinical field.

### Record provenance and exports

The structured record header has three separate clinician actions:

- **View source** opens a full-screen provenance lightbox. Selecting a structured field keeps its contextual highlight visible, supporting a compare-and-verify workflow.
- **PDF** creates a simple, readable one-page pilot record export locally in `exportRecordPdf()` in `src/services/aiClient.ts`. It is intentionally not a signed clinical document or a replacement for an approved facility report template.
- **FHIR** downloads the existing interoperable JSON Bundle. Its basic V1 mapping is in `exportFHIR()` in the same file.

All current exports are client-side pilot exports. Before any production deployment, add authenticated server-side audit logging, organisation-specific document templates, retention controls, and a compliance review.

### Batch triage

`/batch` accepts up to 100 local images or PDFs. It flags filenames containing `blurry`, `fail`, or `error` so the pilot team can exercise the unreadable-document path, then allows retry, removal, and queueing of ready documents. This is a client-side workflow preview; it becomes a real batch processor only after the asynchronous worker and secure source storage milestones are complete.

### Mock versus live API mode

The frontend reads these environment variables at build time:

| Variable | `mock` value | `live` value |
|---|---|---|
| `VITE_AI_MODE` | `mock` | `live` |
| `VITE_AI_BASE_URL` | unused | Render API base URL, without `/api/v1` |
| `VITE_AI_TIMEOUT_MS` | `30000` | `30000` |

In mock mode, `convertDocument()` simulates realistic progress and returns safe fixtures. In live mode, it sends a JSON request to `${VITE_AI_BASE_URL}/api/v1/convert`. The current Node API is a contract stub: it returns the demo record and does not yet upload or process real source bytes.

Never put database URLs, Supabase service-role keys, or model-provider secrets in a `VITE_` variable. Vite publishes every `VITE_` value into the browser bundle.

### Node backend and Supabase

The Node API lives in `backend/` and is independently deployed to Render.

| File | Responsibility |
|---|---|
| `backend/src/server.js` | Starts the Express server and listens on Render's assigned port |
| `backend/src/app.js` | Defines HTTP routes, CORS, request validation, and friendly API responses |
| `backend/src/config/env.js` | Reads environment variables once and exposes safe configuration values |
| `backend/src/infrastructure/database.js` | Creates the server-only PostgreSQL connection pool and health query |
| `backend/src/infrastructure/supabase.js` | Holds the future server-only Supabase client boundary |
| `backend/.env` | Local secrets only; ignored by Git |
| `backend/.env.example` | Safe template committed for the team |

For a persistent Render service, use the Supabase **Session Pooler** URI in `DATABASE_URL`. The URL must contain `.pooler.supabase.com` and port `5432`. Use `CORS_ORIGINS=https://digitmed.vercel.app` in Render production settings.

### Changing the database safely

1. Add a new, numbered SQL file under `supabase/migrations/`.
2. Make additive changes first. Do not drop or rename columns holding clinical data without an approved migration plan.
3. Apply the SQL in a non-production Supabase project first when one exists.
4. Confirm Row Level Security is enabled before creating any client-facing access policy.
5. Record the schema decision and completed checklist item in `docs/PROJECT_CHECKLIST.md`.
6. Update this README with the new table's purpose, relationship, and access model.

### Required verification before every pull request

```powershell
npm run build
cd backend
npm install
node --input-type=module -e "import('./src/app.js').then(({app}) => console.log(typeof app))"
```

Also manually test the happy path, failed conversion (`fail` in a filename), permission-denied camera fallback, a 390px mobile layout, and a desktop layout.

## Run locally

### Frontend

Prerequisite: Node 20.16 or later.

```powershell
npm install
npm run dev
```

Open `http://127.0.0.1:5173`.

Create a production bundle with:

```powershell
npm run build
```

### Node.js API

Prerequisite: Node 20.16 or later.

```powershell
cd backend
npm install
npm run dev
```

Check `http://127.0.0.1:5000/api/v1/health`.

The browser application defaults to `VITE_AI_MODE=mock`, so it works without the API or a model. That is an intentional V1 reliability choice.

## Environment configuration

Copy `.env.example` to `.env` when environment variables are needed.

```dotenv
VITE_AI_MODE=mock
VITE_AI_BASE_URL=http://localhost:5000
VITE_AI_TIMEOUT_MS=30000
VITE_AI_MAX_RETRIES=3

# Add only after Supabase is configured.
VITE_SUPABASE_URL=
VITE_SUPABASE_ANON_KEY=
```

Never commit `.env`, service-role keys, API secrets, patient data, raw NIN values, or production exports.

## Current AI boundary

`src/services/aiClient.ts` is the only client-side model boundary. It contains marked integration points for conversion, confidence, retry, batch work, FHIR export, classification, and service health.

The current mock adapter:

- Takes approximately 4.2 seconds.
- Reports realistic non-linear progress.
- Includes imperfect confidence values to exercise clinical review.
- Fails deliberately for filenames containing `blurry`, `fail`, or `error`.
- Never discards the source file.

## Training harness plan

The runnable, data-free starter harness lives in `training/`. Begin with [training/README.md](training/README.md), then use the JSON schemas and deterministic split script only after facility approval, consent/lawful-basis confirmation, and de-identification review. The entire `training/data/`, `training/runs/`, and `training/models/` directories are intentionally ignored by Git.

### Image preprocessing and redaction

`training/scripts/preprocess.py` is the offline data-preparation step for approved GPU work. It deskews a page, normalises uneven illumination, records blur/resolution quality signals, and applies black redaction rectangles from `redactions.jsonl`. It will fail closed when consent, de-identification review, or explicit human redaction approval is absent. It does **not** attempt automatic PHI detection or claim that redaction has been independently verified.

On an approved Python environment, install `training/requirements.txt`, then run:

```bash
python training/scripts/preprocess.py --manifest training/data/manifest.jsonl --image-root training/data --redactions training/data/redactions.jsonl --output-root training/data/processed --report training/runs/preprocess-report.json
```

Review the generated report and its blocked/flagged items before annotation. The current harness does not automatically crop document edges; that remains a separate, testable preprocessing addition.

### Benchmarking model candidates

The benchmark harness is intentionally model-neutral. `training/scripts/evaluate.py` compares a candidate's JSONL predictions with held-out reviewed labels and outputs character error rate (CER), word error rate (WER), field accuracy, Brier confidence score, and the proportion of fields sent to clinician review. Lower CER, WER, and Brier scores are better; field accuracy is higher-is-better. The fixture adapter is only for validating the measurement pipeline and is not OCR or AI.

```bash
python training/scripts/fixture_baseline.py --labels training/data/annotations.jsonl --output training/runs/fixture-predictions.jsonl
python training/scripts/evaluate.py --labels training/data/annotations.jsonl --predictions training/runs/fixture-predictions.jsonl --output training/runs/benchmark-report.json
```

Run benchmark reports only on the untouched, consented, de-identified test split. Do not select a model or publish an accuracy claim from fixture data, training data, or a non-Nigerian dataset.

### Experiment registry and GPU handoff

Every future run should be registered with `training/scripts/register_experiment.py`. It records the Git commit, de-identified dataset version, configuration path, metrics, checkpoint/export SHA-256 hashes, and explicit approval flags in `training/runs/registry.jsonl` (which Git ignores). An evaluation result alone is not pilot approval: held-out evaluation and clinical review must both be recorded as complete.

`training/Dockerfile` provides a reproducible CUDA/Python starting point for an approved GPU environment. It does not contain data, secrets, or a selected model. Build and run it only in an approved private environment; do not transfer raw clinical images into a public container registry.

### TrOCR baseline: download, drafts, and fine-tuning format

DigitMed's current baseline candidate is [`microsoft/trocr-base-handwritten`](https://huggingface.co/microsoft/trocr-base-handwritten). It is an MIT-licensed `VisionEncoderDecoderModel` for **single handwritten text lines** and ships normal Transformers/safetensors weights—not a GGUF Q4 file. Download it on the approved GPU machine by installing PyTorch for that machine's CUDA version from [PyTorch's official selector](https://pytorch.org/get-started/locally/), then `pip install -r training/requirements-train.txt`. The first run of `infer_trocr.py` downloads the model into Hugging Face's local cache; the official repository is about 2.67 GB including duplicate weight formats.

`training/scripts/infer_trocr.py` creates *draft* JSONL transcripts only. Every generated line is marked `needs_human_verification`; drafts must never be fine-tuning labels. After annotation review, `build_trocr_jsonl.py` emits the line-level `image` + `text` JSONL files expected by a standard Hugging Face dataset/training workflow. It only admits records whose manifest and annotation are both verified.

Use this candidate first for a zero-shot/draft-transcription benchmark. Fine-tuning on 29 examples is not defensible; more data can support annotation acceleration, but only a consented, de-identified, writer/facility-safe held-out dataset can support selection or an accuracy claim. CRAFT is not a mandatory TrOCR dependency: it is one possible text-region detector. We must benchmark line/page segmentation separately because handwritten clinical pages are harder than CRAFT's typical scene-text target.

### Controlled local intake from Drive exports

Export a small approved image sample from Drive to a local folder outside the repository, then run:

```bash
python training/scripts/intake_local_images.py --source-dir "C:/path/to/exported-images" --source-group old_handwriting_split_1 --limit 10
```

This copies images to the ignored `training/data/images/` directory under anonymous IDs, writes `manifest-draft.jsonl` without personal filenames, and writes the sensitive original-name mapping only to ignored `training/data/restricted/`. It deliberately marks all samples `not_approved` and `redaction_reviewed: false`; a human must complete those gates before preprocessing, transcription, annotation, or training.

### Do not begin with GGUF

GGUF is normally a compressed deployment format for local inference. It is not the dataset format or training strategy for handwriting recognition. DigitMed needs a pipeline:

```text
quality assessment → document classification → handwriting recognition
→ clinical structuring → confidence/provenance → clinician review
```

An offline GGUF component may later help with small local text-structuring tasks, but it must follow evidence from the actual benchmark.

### Data required before model training

The research audit records around 29 verified image-to-text pairs. That is not enough for a useful clinical handwriting model. The first defensible milestone is 1,000 consented, de-identified, verified labelled samples, diverse by facility, clinical speciality, document type, capture quality, and handwriting style.

Each dataset item should have:

- Secure original image and a de-identified working derivative.
- Consent/lawful-basis, facility, document type, and annotation status.
- Verified transcription.
- Structured fields when available: complaints, diagnosis, medication, dose, frequency, duration, and investigations.
- Field polygons/bounding boxes where feasible.
- Metadata suitable for bias and performance analysis, without unnecessary patient identifiers.

### Training and evaluation requirements

- Split data by facility and writer where possible. Never let the same writer/document leak from training into the test set.
- Record character error rate, word error rate, field extraction accuracy, calibration, review workload, latency, and cost per page.
- Benchmark against baseline services/models on a held-out Nigerian clinical dataset before publishing an accuracy claim.
- Train only in an approved, access-controlled GPU environment with de-identified working data.
- Preserve reproducible configurations, model versions, dataset manifests, and experiment outcomes.

The current local GPU is a Quadro M1000M with 2 GB VRAM. It is unsuitable for meaningful modern handwriting or vision-language model fine-tuning. The harness will be designed to copy to stronger GPU infrastructure later without changing the product contract.

## Supabase plan

Supabase is selected for the persistent product backend, but it will be introduced safely in stages.

1. Create a Supabase project in an approved region.
2. Define database migrations for facilities, users, documents, jobs, records, fields, provenance, consent, and audit events.
3. Create private Storage buckets for originals and safe derivatives.
4. Enable Row Level Security before any real data is uploaded.
5. Use signed URLs and a server-side conversion worker. The frontend must never receive a service-role key.
6. Add Google OAuth and email/password only when V1 direct-access mode is retired.
7. Add role-based policies only after role responsibilities are explicitly approved.

## Authentication decision

Authentication is deferred. The project will later use **Supabase Auth**, which can support Google OAuth, email/password, magic links, and other identity providers. “Passport Google auth” is broadly the right idea: a trusted sign-in provider verifies identity so DigitMed does not need to build password systems itself.

For now, no one should assume the open pilot protects real clinical data. Do not upload identifiable records until access controls and facility agreements are live.

## Compliance and safety guardrails

- Use Nigeria Data Protection Act 2023 and GAID 2025 language. Do not make outdated NDPR-compliant claims.
- Health data is sensitive personal data. Obtain the required consent/lawful basis and facility approvals before data collection or model training.
- Keep identity mappings and unredacted originals controlled and access-limited.
- De-identify derivatives before model training and before any approved cross-border compute use.
- Require human clinical review. No automated diagnosis, treatment recommendation, or unreviewed EMR write-back.
- Never describe V1 as a medical device or make clinical-accuracy claims until tested in the intended setting.

## GitHub workflow

When the safe-directory setting is resolved and a GitHub repository exists:

```powershell
git add .
git commit -m "feat: initialise DigitMed pilot"
git branch -M main
git remote add origin https://github.com/YOUR-ORG/digitmed.git
git push -u origin main
```

Before pushing, confirm `.env`, raw patient data, model weights containing sensitive data, and any temporary exports are ignored.

## Vercel deployment

1. Sign in to Vercel with the GitHub account that owns the repository.
2. Click **Add New → Project**, then import `digitmed`.
3. Vercel detects Vite. Keep build command `npm run build` and output directory `dist`.
4. Add `VITE_AI_MODE=mock` for the initial demo deployment.
5. Deploy. `vercel.json` handles SPA route rewrites.
6. Test direct navigation to `/dashboard`, `/upload`, and `/records/8842`.

## Render deployment

1. Sign in to Render and create a **Web Service** from the same GitHub repository.
2. Set root directory to `backend`.
3. Set build command to `npm ci`.
4. Set start command to `npm start`.
5. Test `/api/v1/health` after deployment.
6. Only switch the frontend to `VITE_AI_MODE=live` when the deployed API and its error/retry handling are verified.

## Maintainer rules

- Keep `AWIBI_DIGITMED_V1_BUILD_SPEC.md` as the visual and interaction authority for V1.
- Update this README and `docs/PROJECT_CHECKLIST.md` whenever architecture, deployment, privacy, model, or product decisions change.
- Prefer working, reviewable flows over unverified claims.
- Preserve the original source document through every conversion state.
- Never fabricate model confidence or clinical certainty.

## License and ownership

Add a licence only after the organisation decides whether this repository is private/proprietary, source-available, or open source. Until then, treat it as proprietary project material.
