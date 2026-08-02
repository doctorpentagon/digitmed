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
export async function classifyType(value: string) { /* [AI-INTEGRATION-POINT] POST /api/v1/classify */ return value }
export async function health() { /* [AI-INTEGRATION-POINT] GET /api/v1/health */ return { status: 'mock' } }
