-- PC Architect — Epic 7 (Community & Cloud Sync) schema.
-- Run this once in your Supabase project's SQL Editor.

create table if not exists community_builds (
    id uuid primary key default gen_random_uuid(),
    user_id uuid not null,
    author_name text not null,
    name text not null,
    parts_json text not null,
    price numeric not null default 0,
    overall_score int not null default 0,
    created_at timestamptz not null default now()
);

create table if not exists favorites (
    user_id uuid not null,
    build_id uuid not null references community_builds(id) on delete cascade,
    created_at timestamptz not null default now(),
    primary key (user_id, build_id)
);

alter table community_builds enable row level security;
alter table favorites enable row level security;

-- Anyone (including anonymous) can read the public feed and favorite counts.
create policy "community_builds are publicly readable"
    on community_builds for select
    using (true);

create policy "favorites are publicly readable"
    on favorites for select
    using (true);

-- Only the authenticated owner can publish/edit/delete their own builds.
create policy "users can publish their own builds"
    on community_builds for insert
    with check (auth.uid() = user_id);

create policy "users can update their own builds"
    on community_builds for update
    using (auth.uid() = user_id);

create policy "users can delete their own builds"
    on community_builds for delete
    using (auth.uid() = user_id);

-- Only the authenticated owner can favorite/unfavorite as themselves.
create policy "users can favorite as themselves"
    on favorites for insert
    with check (auth.uid() = user_id);

create policy "users can remove their own favorites"
    on favorites for delete
    using (auth.uid() = user_id);
