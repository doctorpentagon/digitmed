import pg from 'pg'
import { env, hasDatabaseConfig } from '../config/env.js'

// Direct Postgres access is server-only. The browser must use neither this URL nor a DB password.
export const pool = hasDatabaseConfig
  ? new pg.Pool({ connectionString: env.databaseUrl, ssl: { rejectUnauthorized: false } })
  : null

export async function databaseHealth() {
  if (!pool) return 'not-configured'
  await pool.query('select 1')
  return 'connected'
}
