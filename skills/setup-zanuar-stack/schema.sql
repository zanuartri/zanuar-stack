-- zanuar-stack ticket store. Default path: ~/.orca/tickets/tickets.db
PRAGMA journal_mode = WAL;

CREATE TABLE IF NOT EXISTS stories (
  id    TEXT PRIMARY KEY,          -- e.g. S-12
  title TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS tickets (
  id         INTEGER PRIMARY KEY AUTOINCREMENT,
  repo       TEXT NOT NULL,        -- absolute repo path or a stable name
  story      TEXT REFERENCES stories(id),
  title      TEXT NOT NULL,
  goal       TEXT,
  acceptance TEXT,
  verify     TEXT,
  scope      TEXT,
  status     TEXT NOT NULL DEFAULT 'todo'
             CHECK (status IN ('todo','in-progress','review','needs-you','blocked','done')),
  branch     TEXT,
  pr_url     TEXT,
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

CREATE TABLE IF NOT EXISTS decisions (   -- used by the decision-log skill
  id       INTEGER PRIMARY KEY AUTOINCREMENT,
  ts       TEXT NOT NULL DEFAULT (datetime('now')),
  ticket   INTEGER REFERENCES tickets(id),
  phase    TEXT,
  decision TEXT NOT NULL,
  why      TEXT,
  evidence TEXT,
  result   TEXT
);

CREATE INDEX IF NOT EXISTS tickets_repo_status ON tickets(repo, status);
CREATE INDEX IF NOT EXISTS runs_ticket ON runs(ticket);
