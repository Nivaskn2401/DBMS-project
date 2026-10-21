-- SQLite schema used by library_app.py
PRAGMA foreign_keys = ON;
CREATE TABLE IF NOT EXISTS books (
  book_id INTEGER PRIMARY KEY AUTOINCREMENT,
  title TEXT NOT NULL,
  author TEXT NOT NULL,
  category TEXT NOT NULL DEFAULT 'General',
  isbn TEXT UNIQUE,
  copies INTEGER NOT NULL DEFAULT 1 CHECK(copies >= 0),
  available INTEGER NOT NULL DEFAULT 1 CHECK(available >= 0 AND available <= copies)
);
CREATE TABLE IF NOT EXISTS members (
  member_id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT NOT NULL,
  email TEXT NOT NULL UNIQUE,
  phone TEXT,
  joined_on TEXT NOT NULL DEFAULT (DATE('now'))
);
CREATE TABLE IF NOT EXISTS issues (
  issue_id INTEGER PRIMARY KEY AUTOINCREMENT,
  book_id INTEGER NOT NULL REFERENCES books(book_id) ON DELETE RESTRICT,
  member_id INTEGER NOT NULL REFERENCES members(member_id) ON DELETE RESTRICT,
  issue_date TEXT NOT NULL,
  due_date TEXT NOT NULL,
  return_date TEXT
);
CREATE INDEX IF NOT EXISTS idx_issues_member ON issues(member_id);
CREATE INDEX IF NOT EXISTS idx_issues_book ON issues(book_id);
