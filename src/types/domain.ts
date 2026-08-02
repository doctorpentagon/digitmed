export type JobStatus = 'captured' | 'queued' | 'uploading' | 'processing' | 'needs_review' | 'done' | 'failed'
export type Role = 'clinic' | 'hospital' | 'developer'
export interface ClinicalField { label: string; value: string; confidence: number | null; bbox?: [number, number, number, number] }
export interface RecordSection { title: string; fields: ClinicalField[] }
export interface ClinicalRecord { id: string; documentType: string; patient: { name: string; age: string; sex: string; patientRef: string }; overallConfidence: number | null; sections: RecordSection[] }
export interface ConversionJob { id: string; name: string; docType: string; status: JobStatus; progress: number; createdAt: string; history: {status: JobStatus; at: string}[]; record?: ClinicalRecord; sourceUrl?: string }
