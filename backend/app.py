from flask import Flask, jsonify, request
from flask_cors import CORS
from datetime import datetime, timezone

app = Flask(__name__)
CORS(app)

RECORD = {
    "id": "8842",
    "document_type": "outpatient_note",
    "overall_confidence": 0.98,
    "patient": {"name": "Amina Yusuf", "age": "31 years", "sex": "Female", "patient_ref": "LGC-04821"},
    "sections": [
        {"title": "Presenting complaints", "fields": [{"label": "Complaints", "value": "Three-day febrile illness with an episode of seizure, limb stiffening and post-ictal loss of consciousness.", "confidence": 0.98}]},
        {"title": "Clinical impression", "fields": [{"label": "Diagnosis", "value": "First seizure episode with post-ictal loss of consciousness.", "confidence": 0.96}]},
        {"title": "Management plan", "fields": [{"label": "Medication", "value": "Sodium valproate 200 mg, twice daily for 14 days.", "confidence": 0.86}, {"label": "Investigation", "value": "Full blood count and serum electrolytes.", "confidence": 0.92}]}
    ]
}

@app.get('/api/v1/health')
def health():
    return jsonify({"status": "healthy", "service": "digitmed-api", "mode": "demo"})

@app.post('/api/v1/convert')
def convert():
    file = request.files.get('file')
    if not file:
        return jsonify({"error": {"code": "INVALID_FILE", "message": "A document file is required."}}), 400
    lower = file.filename.lower()
    if any(token in lower for token in ('blurry', 'fail', 'error')):
        return jsonify({"error": {"code": "UNREADABLE_IMAGE", "message": "We could not read this image clearly enough."}}), 422
    return jsonify({"job_id": "job_8842", "status": "needs_review", "duration_ms": 4210, "model_version": "digitmed-demo-v0.1", **RECORD, "created_at": datetime.now(timezone.utc).isoformat()})

@app.post('/api/v1/convert/<job_id>/retry')
def retry(job_id):
    return jsonify({"job_id": job_id, "status": "queued"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
