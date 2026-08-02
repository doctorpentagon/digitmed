import cors from 'cors'
import express from 'express'
import { env, hasSupabaseConfig } from './config/env.js'
import { databaseHealth } from './infrastructure/database.js'
import { demoRecord } from './fixtures/record.js'

export const app = express()
app.use(cors({ origin: env.nodeEnv === 'production' ? env.corsOrigins : true }))
app.use(express.json({ limit: '2mb' }))

app.get('/api/v1/health', async (_request, response) => {
  try {
    response.json({ status: 'healthy', service: 'digitmed-api', mode: hasSupabaseConfig ? 'supabase-ready' : 'demo', database: await databaseHealth() })
  } catch {
    response.status(503).json({ status: 'degraded', service: 'digitmed-api', database: 'unreachable' })
  }
})

app.post('/api/v1/convert', (request, response) => {
  const filename = String(request.body?.filename ?? '')
  if (!filename) return response.status(400).json({ error: { code: 'INVALID_FILE', message: 'A document filename is required.' } })
  if (/blurry|fail|error/i.test(filename)) return response.status(422).json({ error: { code: 'UNREADABLE_IMAGE', message: 'We could not read this image clearly enough.' } })
  return response.json({ job_id: 'job_8842', status: 'needs_review', duration_ms: 4210, model_version: 'digitmed-demo-v0.1', ...demoRecord, created_at: new Date().toISOString() })
})

app.post('/api/v1/convert/:jobId/retry', (request, response) => response.json({ job_id: request.params.jobId, status: 'queued' }))

app.use((_request, response) => response.status(404).json({ error: { code: 'NOT_FOUND', message: 'This DigitMed API route does not exist.' } }))
