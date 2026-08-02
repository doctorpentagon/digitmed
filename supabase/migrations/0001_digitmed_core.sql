-- Initial DigitMed clinical-document data model.
-- Apply through the Supabase CLI only after the project, privacy model, and RLS review are approved.

create extension if not exists pgcrypto;

create table if not exists public.facilities (
  id uuid primary key default gen_random_uuid(),
  name text not null,
  created_at timestamptz not null default now()
);

create table if not exists public.documents (
  id uuid primary key default gen_random_uuid(),
  facility_id uuid references public.facilities(id),
  source_storage_path text not null,
  document_type text,
  status text not null check (status in ('captured','queued','uploading','processing','needs_review','done','failed')),
  created_at timestamptz not null default now()
);

create table if not exists public.records (
  id uuid primary key default gen_random_uuid(),
  document_id uuid not null unique references public.documents(id) on delete cascade,
  structured_data jsonb not null default '{}'::jsonb,
  overall_confidence numeric(4,3),
  reviewed_at timestamptz,
  created_at timestamptz not null default now()
);

create table if not exists public.audit_events (
  id uuid primary key default gen_random_uuid(),
  facility_id uuid references public.facilities(id),
  event_type text not null,
  entity_type text not null,
  entity_id uuid,
  metadata jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now()
);

alter table public.facilities enable row level security;
alter table public.documents enable row level security;
alter table public.records enable row level security;
alter table public.audit_events enable row level security;

-- No policies are included intentionally. Define and review membership-based policies
-- before allowing client access or storing identifiable data.
