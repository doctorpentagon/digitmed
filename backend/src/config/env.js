import 'dotenv/config'

export const env = {
  nodeEnv: process.env.NODE_ENV ?? 'development',
  port: Number(process.env.PORT ?? 5000),
  databaseUrl: process.env.DATABASE_URL,
  corsOrigins: (process.env.CORS_ORIGINS ?? 'http://127.0.0.1:5173').split(',').map(origin => origin.trim()).filter(Boolean),
  supabaseUrl: process.env.SUPABASE_URL,
  supabaseServiceRoleKey: process.env.SUPABASE_SERVICE_ROLE_KEY,
}

export const hasSupabaseConfig = Boolean(env.supabaseUrl && env.supabaseServiceRoleKey)
export const hasDatabaseConfig = Boolean(env.databaseUrl)
