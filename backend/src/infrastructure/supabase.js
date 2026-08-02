import { createClient } from '@supabase/supabase-js'
import { env, hasSupabaseConfig } from '../config/env.js'

// The service-role key belongs only on the server. It must never be exposed to Vite.
export const supabase = hasSupabaseConfig
  ? createClient(env.supabaseUrl, env.supabaseServiceRoleKey, { auth: { persistSession: false } })
  : null
