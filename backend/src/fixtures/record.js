export const demoRecord = {
  id: '8842',
  document_type: 'outpatient_note',
  overall_confidence: 0.98,
  patient: { name: 'Amina Yusuf', age: '31 years', sex: 'Female', patient_ref: 'LGC-04821' },
  sections: [
    { title: 'Presenting complaints', fields: [{ label: 'Complaints', value: 'Three-day febrile illness with an episode of seizure, limb stiffening and post-ictal loss of consciousness.', confidence: 0.98 }] },
    { title: 'Clinical impression', fields: [{ label: 'Diagnosis', value: 'First seizure episode with post-ictal loss of consciousness.', confidence: 0.96 }] },
    { title: 'Management plan', fields: [{ label: 'Medication', value: 'Sodium valproate 200 mg, twice daily for 14 days.', confidence: 0.86 }, { label: 'Investigation', value: 'Full blood count and serum electrolytes.', confidence: 0.92 }] },
  ],
}
