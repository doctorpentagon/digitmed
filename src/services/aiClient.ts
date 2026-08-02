import { canonicalRecord } from '../lib/fixtures'
import type { ClinicalRecord } from '../types/domain'

const delay = (ms: number) => new Promise(resolve => window.setTimeout(resolve, ms))
const mode = import.meta.env.VITE_AI_MODE ?? 'mock'
const baseUrl = (import.meta.env.VITE_AI_BASE_URL ?? 'http://127.0.0.1:5000').replace(/\/$/, '')

export async function convertDocument({ file, docType, onProgress }: { file: File; docType: string; onProgress: (value: number) => void }): Promise<ClinicalRecord> {
  // [AI-INTEGRATION-POINT] POST /api/v1/convert
  if (mode === 'live') return liveConvert({ file, docType, onProgress })
  if (/blurry|fail|error/i.test(file.name)) throw new Error('UNREADABLE_IMAGE')
  const points = [8, 23, 41, 58, 74, 87, 96, 100]
  for (const point of points) { await delay(point === 96 ? 900 : 470); onProgress(point) }
  return { ...canonicalRecord, documentType: docType }
}

async function liveConvert({ file, docType, onProgress }: { file: File; docType: string; onProgress: (value: number) => void }): Promise<ClinicalRecord> {
  onProgress(8)
  const controller = new AbortController()
  const timeout = window.setTimeout(() => controller.abort(), Number(import.meta.env.VITE_AI_TIMEOUT_MS ?? 30000))
  try {
    const response = await fetch(`${baseUrl}/api/v1/convert`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ filename: file.name, documentType: docType }), signal: controller.signal })
    const payload = await response.json()
    if (!response.ok) throw new Error(payload?.error?.code ?? 'CONVERSION_UNAVAILABLE')
    onProgress(100)
    return { id: payload.id, documentType: payload.document_type, overallConfidence: payload.overall_confidence, patient: { name: payload.patient.name, age: payload.patient.age, sex: payload.patient.sex, patientRef: payload.patient.patient_ref }, sections: payload.sections }
  } finally { window.clearTimeout(timeout) }
}
export async function getConfidence() { /* [AI-INTEGRATION-POINT] confidence included in response */ return canonicalRecord.overallConfidence }
export async function reprocess() { /* [AI-INTEGRATION-POINT] POST /api/v1/convert/:id/retry */ return true }
export async function batchConvert() { /* [AI-INTEGRATION-POINT] POST /api/v1/batch */ return true }
export function exportFHIR(record: ClinicalRecord) { // [AI-INTEGRATION-POINT] POST /api/v1/records/:id/fhir
  return { resourceType: 'Bundle', type: 'collection', entry: [{ resource: { resourceType: 'Patient', id: record.patient.patientRef, name: [{ text: record.patient.name }] } }, { resource: { resourceType: 'DocumentReference', status: 'current', description: record.documentType } }] }
}
export function exportRecordPdf(record: ClinicalRecord) {
  const text = ['DigitMed - Structured Patient Record', `Patient: ${record.patient.name} | ${record.patient.age} | ${record.patient.sex}`, `Reference: ${record.patient.patientRef}`, `Document type: ${record.documentType}`, '', ...record.sections.flatMap(section => [section.title.toUpperCase(), ...section.fields.map(field => `${field.label}: ${field.value}`), '']), `Overall confidence: ${Math.round((record.overallConfidence || 0) * 100)}%`, 'Clinician review is required before clinical use.'].map(line => line.replace(/[\\()]/g, '\\$&').replace(/[^\x20-\x7E]/g, ' '))
  const stream = `BT\n/F1 16 Tf\n50 790 Td\n(${text[0]}) Tj\n/F1 10 Tf\n${text.slice(1, 48).map(line => `0 -16 Td\n(${line.slice(0, 110)}) Tj`).join('\n')}\nET`
  const objects = ['<< /Type /Catalog /Pages 2 0 R >>', '<< /Type /Pages /Kids [3 0 R] /Count 1 >>', '<< /Type /Page /Parent 2 0 R /MediaBox [0 0 595 842] /Resources << /Font << /F1 5 0 R >> >> /Contents 4 0 R >>', `<< /Length ${stream.length} >>\nstream\n${stream}\nendstream`, '<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>']
  let pdf = '%PDF-1.4\n'; const offsets = [0]
  objects.forEach((object, index) => { offsets.push(pdf.length); pdf += `${index + 1} 0 obj\n${object}\nendobj\n` })
  const xref = pdf.length; pdf += `xref\n0 ${objects.length + 1}\n0000000000 65535 f \n${offsets.slice(1).map(offset => `${String(offset).padStart(10, '0')} 00000 n `).join('\n')}\ntrailer\n<< /Size ${objects.length + 1} /Root 1 0 R >>\nstartxref\n${xref}\n%%EOF`
  return new Blob([pdf], { type: 'application/pdf' })
}
export async function classifyType(value: string) { /* [AI-INTEGRATION-POINT] POST /api/v1/classify */ return value }
export async function health() { /* [AI-INTEGRATION-POINT] GET /api/v1/health */ return { status: 'mock' } }
