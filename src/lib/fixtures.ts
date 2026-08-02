import type { ClinicalRecord, ConversionJob } from '../types/domain'

export const canonicalRecord: ClinicalRecord = {
  id: '8842', documentType: 'Outpatient note', overallConfidence: .98,
  patient: { name: 'Amina Yusuf', age: '31 years', sex: 'Female', patientRef: 'LGC-04821' },
  sections: [
    { title: 'Presenting complaints', fields: [{ label: 'Complaints', value: 'Three-day febrile illness with an episode of seizure, limb stiffening and post-ictal loss of consciousness.', confidence: .98, bbox: [10, 18, 74, 20] }] },
    { title: 'Clinical impression', fields: [{ label: 'Diagnosis', value: 'First seizure episode with post-ictal loss of consciousness.', confidence: .96, bbox: [12, 42, 70, 13] }] },
    { title: 'Management plan', fields: [{ label: 'Medication', value: 'Sodium valproate 200 mg, twice daily for 14 days.', confidence: .86, bbox: [10, 61, 76, 14] }, { label: 'Investigation', value: 'Full blood count and serum electrolytes.', confidence: .92, bbox: [10, 78, 66, 12] }] }
  ]
}

export const recentJobs: ConversionJob[] = [
  { id: 'job_8842', name: 'OPD_note_Amina_Yusuf.jpg', docType: 'Outpatient note', status: 'needs_review', progress: 100, createdAt: 'Today, 10:42 AM', history: [], record: canonicalRecord },
  { id: 'job_8841', name: 'Prescription_Kazeem.jpg', docType: 'Prescription', status: 'done', progress: 100, createdAt: 'Today, 9:16 AM', history: [] },
  { id: 'job_8840', name: 'Ward_round_notes.jpg', docType: 'Admission note', status: 'done', progress: 100, createdAt: 'Yesterday, 4:22 PM', history: [] },
]
