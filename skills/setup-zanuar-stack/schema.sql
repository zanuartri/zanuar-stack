-- zanuar-stack ticket store. Default path: ~/.orca/tickets/tickets.db
PRAGMA journal_mode = WAL;

CREATE TABLE IF NOT EXISTS stories (
  id    TEXT PRIMARY KEY,          -- e.g. S-12
  title TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS tickets (
  id         INTEGER PRIMARY KEY AUTOINCREMENT,
  repo       TEXT NOT NULL,        -- the repo's absolute path with forward slashes
  story      TEXT REFERENCES stories(id),
  title      TEXT NOT NULL,
  goal       TEXT,
  acceptance TEXT,
  verify     TEXT,
  scope      TEXT,
  status     TEXT NOT NULL DEFAULT 'todo'
             CHECK (status IN ('todo','queued','in-progress','review','needs-you','blocked','done','canceled')),
  branch     TEXT,
  base       TEXT,                  -- NULL = use the repo's integration branch
  pr_url     TEXT,
  autonomy   TEXT CHECK (autonomy IN ('ask','review','merge')),  -- NULL = use repo_settings
  land       TEXT CHECK (land IN ('pr','local')),                -- NULL = use repo_settings
  roles      TEXT,                  -- JSON overrides for worker and reviewer
  manager_dispatch TEXT,           -- Orca dispatch id of the owning manager; pr_watch mails it
  depends_on TEXT,                 -- ticket ids this one waits on, comma list: '12,14'
  fix_rounds INTEGER NOT NULL DEFAULT 0,
  created_at TEXT NOT NULL DEFAULT (datetime('now')),
  started_at TEXT,
  review_at  TEXT,
  done_at    TEXT
);

CREATE TABLE IF NOT EXISTS runs (
  id      INTEGER PRIMARY KEY AUTOINCREMENT,
  ticket  INTEGER NOT NULL REFERENCES tickets(id),
  role    TEXT NOT NULL CHECK (role IN ('manager','worker','reviewer')),
  harness TEXT NOT NULL,           -- claude | codex | omp | commandcode | ...
  model   TEXT,
  effort  TEXT,
  mode    TEXT NOT NULL CHECK (mode IN ('orca','headless')),
  started TEXT NOT NULL DEFAULT (datetime('now')),
  ended   TEXT,
  result  TEXT                     -- PASS | FIX | done | blocked | failed | free text
);

CREATE TABLE IF NOT EXISTS repo_config (
  repo    TEXT NOT NULL,           -- '*' = machine-wide default
  role    TEXT NOT NULL CHECK (role IN ('manager','worker','reviewer')),
  harness TEXT NOT NULL,
  model   TEXT,
  effort  TEXT,
  mode    TEXT NOT NULL DEFAULT 'orca' CHECK (mode IN ('orca','headless')),
  PRIMARY KEY (repo, role)
);

CREATE TABLE IF NOT EXISTS decisions (   -- orchestration and manager decision history
  id       INTEGER PRIMARY KEY AUTOINCREMENT,
  ts       TEXT NOT NULL DEFAULT (datetime('now')),
  ticket   INTEGER REFERENCES tickets(id),
  phase    TEXT,
  decision TEXT NOT NULL,
  why      TEXT,
  evidence TEXT,
  result   TEXT
);

CREATE TABLE IF NOT EXISTS repo_settings (   -- how far agents go alone; repo='*' = machine default
  repo     TEXT PRIMARY KEY,
  autonomy TEXT NOT NULL DEFAULT 'review' CHECK (autonomy IN ('ask','review','merge')),
  land     TEXT NOT NULL DEFAULT 'pr' CHECK (land IN ('pr','local')),
  base     TEXT                     -- NULL = use the GitHub default branch
);
INSERT OR IGNORE INTO repo_settings(repo) VALUES ('*');

CREATE TABLE IF NOT EXISTS pr_watch (        -- last seen state per PR, owned by skills/watch-pr/pr_watch.py
  pr_url     TEXT PRIMARY KEY,
  snapshot   TEXT NOT NULL,                 -- JSON
  updated_at TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS tickets_repo_status ON tickets(repo, status);
CREATE INDEX IF NOT EXISTS runs_ticket ON runs(ticket);

CREATE TABLE IF NOT EXISTS products (
  id                   TEXT PRIMARY KEY,   -- e.g. torchlight
  repo                 TEXT,
  base_branch          TEXT,
  staging_target       TEXT,
  prod_target          TEXT,
  deploy_staging_skill TEXT,
  smoke_skill          TEXT,
  deploy_prod_skill    TEXT,
  merge_rule           TEXT,
  created_at           TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS features (
  id         TEXT PRIMARY KEY,             -- e.g. F-3
  title      TEXT NOT NULL,
  product    TEXT REFERENCES products(id),
  stage      TEXT NOT NULL DEFAULT 'spec'
             CHECK (stage IN ('spec','design','dev','deploy-staging','test','deploy-prod','live')),
  flag_ui    INTEGER NOT NULL DEFAULT 0,
  flag_arch  INTEGER NOT NULL DEFAULT 0,
  flag_ai    INTEGER NOT NULL DEFAULT 0,
  prd        TEXT,
  acceptance TEXT,
  created_at TEXT NOT NULL DEFAULT (datetime('now')),
  updated_at TEXT,
  closed_at  TEXT
);

CREATE TABLE IF NOT EXISTS tasks (
  id         INTEGER PRIMARY KEY AUTOINCREMENT,
  feature_id TEXT REFERENCES features(id),
  kind       TEXT NOT NULL
             CHECK (kind IN ('design','review-arch','review-ai','deploy-staging','test','deploy-prod')),
  assignee   TEXT,
  status     TEXT NOT NULL DEFAULT 'todo'
             CHECK (status IN ('todo','doing','needs-you','done','failed')),
  brief      TEXT,
  result     TEXT,
  links      TEXT,
  created_at TEXT NOT NULL DEFAULT (datetime('now')),
  started_at TEXT,
  done_at    TEXT
);

-- append-only: never UPDATE or DELETE rows
CREATE TABLE IF NOT EXISTS events (
  id         INTEGER PRIMARY KEY AUTOINCREMENT,
  feature_id TEXT REFERENCES features(id),
  actor      TEXT,
  kind       TEXT,
  note       TEXT,
  at         TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_events_feature ON events(feature_id);
CREATE INDEX IF NOT EXISTS idx_tasks_feature_status ON tasks(feature_id, status);
