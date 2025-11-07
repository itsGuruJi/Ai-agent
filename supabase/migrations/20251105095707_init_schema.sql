-- === USERS TABLE ===
create table if not exists users (
  id uuid primary key default gen_random_uuid(),
  email text unique,
  role text,
  org_id int,
  created_at timestamptz default now()
);

-- === SHEETS_ROWS TABLE ===
create table if not exists sheets_rows (
  id uuid primary key default gen_random_uuid(),
  org_id int not null,
  sheet_row_id text,
  data jsonb,
  created_at timestamptz default now(),
  updated_at timestamptz default now()
);

-- === AGENT_TASKS TABLE ===
create table if not exists agent_tasks (
  id uuid primary key default gen_random_uuid(),
  org_id int,
  task_type text,
  payload jsonb,
  status text default 'pending',
  created_at timestamptz default now()
);

-- === AUDIT_LOG TABLE ===
create table if not exists audit_log (
  id uuid primary key default gen_random_uuid(),
  actor text,
  action text,
  detail jsonb,
  created_at timestamptz default now()
);

-- === ENABLE ROW LEVEL SECURITY ===
alter table sheets_rows enable row level security;

-- === BASIC RLS POLICIES (MVP) ===
create policy "org_select" on sheets_rows
  for select using (
    org_id = (current_setting('jwt.claims.org_id'))::int
  );

create policy "org_insert" on sheets_rows
  for insert with check (
    org_id = (current_setting('jwt.claims.org_id'))::int
  );
