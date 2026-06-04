-- ============================================================
-- CompoundPath — Supabase schema
-- Run this in: Supabase dashboard → SQL Editor → New query
-- ============================================================

-- 1. Profiles (one per user, extends auth.users)
create table if not exists public.profiles (
  id          uuid primary key references auth.users(id) on delete cascade,
  username    text unique not null,
  age         integer,
  bio         text,
  created_at  timestamptz default now()
);

-- 2. Portfolios
create table if not exists public.portfolios (
  id           uuid primary key default gen_random_uuid(),
  user_id      uuid not null references public.profiles(id) on delete cascade,
  name         text not null,
  description  text,
  is_public    boolean default false,
  instruments  jsonb not null default '[]',
  created_at   timestamptz default now()
);

-- 3. Row Level Security
alter table public.profiles  enable row level security;
alter table public.portfolios enable row level security;

-- Profiles: anyone can read; only owner can write
create policy "public read profiles"
  on public.profiles for select using (true);

create policy "users insert own profile"
  on public.profiles for insert with check (auth.uid() = id);

create policy "users update own profile"
  on public.profiles for update using (auth.uid() = id);

-- Portfolios: owner can do everything; public ones readable by all
create policy "owner full access portfolios"
  on public.portfolios for all using (auth.uid() = user_id);

create policy "public portfolios readable"
  on public.portfolios for select using (is_public = true);
