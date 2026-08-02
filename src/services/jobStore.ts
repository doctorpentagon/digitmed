import type { ConversionJob } from '../types/domain'
const key = 'digitmed.jobs'
export function loadJobs(): ConversionJob[] { try { return JSON.parse(localStorage.getItem(key) || '[]') } catch { return [] } }
export function saveJobs(jobs: ConversionJob[]) { localStorage.setItem(key, JSON.stringify(jobs)) }
export async function persistSource(file: File) { // IndexedDB source-file preservation for V1 resilience
  return new Promise<void>((resolve, reject) => { const request = indexedDB.open('digitmed', 1); request.onupgradeneeded = () => request.result.createObjectStore('sources'); request.onsuccess = () => { const tx = request.result.transaction('sources', 'readwrite'); tx.objectStore('sources').put(file, file.name); tx.oncomplete = () => resolve(); tx.onerror = () => reject(tx.error) }; request.onerror = () => reject(request.error) })
}
