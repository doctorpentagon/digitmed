import { canonicalRecord } from '../lib/fixtures'
import type { ClinicalRecord } from '../types/domain'

const delay = (ms: number) => new Promise(resolve => window.setTimeout(resolve, ms))

export async function convertDocument({ file, docType, onProgress }: { file: File; docType: string; onProgress: (value: number) => void }): Promise<ClinicalRecord> {
  // [AI-INTEGRATION-POINT] POST /api/v1/convert
  if (/blurry|fail|error/i.test(file.name)) throw new Error('UNREADABLE_IMAGE')
  const points = [8, 23, 41, 58, 74, 87, 96, 100]
  for (const point of points) { await delay(point === 96 ? 900 : 470); onProgress(point) }
  return { ...canonicalRecord, documentType: docType }
}
export async function getConfidence() { /* [AI-INTEGRATION-POINT] confidence included in response */ return canonicalRecord.overallConfidence }
export async function reprocess() { /* [AI-INTEGRATION-POINT] POST /api/v1/convert/:id/retry */ return true }
export async function batchConvert() { /* [AI-INTEGRATION-POINT] POST /api/v1/batch */ return true }
export function exportFHIR(record: ClinicalRecord) { // [AI-INTEGRATION-POINT] POST /api/v1/records/:id/fhir
  return { resourceType: 'Bundle', type: 'collection', entry: [{ resource: { resourceType: 'Patient', id: record.patient.patientRef, name: [{ text: record.patient.name }] } }, { resource: { resourceType: 'DocumentReference', status: 'current', description: record.documentType } }] }
}
export async function classifyType(value: string) { /* [AI-INTEGRATION-POINT] POST /api/v1/classify */ return value }
export async function health() { /* [AI-INTEGRATION-POINT] GET /api/v1/health */ return { status: 'mock' } }
