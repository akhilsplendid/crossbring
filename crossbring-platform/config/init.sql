-- Initialize schema and tables for Crossbring job platform
CREATE TABLE IF NOT EXISTS jobs (
  id SERIAL PRIMARY KEY,
  title TEXT NOT NULL,
  company TEXT,
  location TEXT,
  salary_min NUMERIC,
  salary_max NUMERIC,
  posted_date DATE,
  description TEXT,
  source TEXT,
  created_at TIMESTAMP DEFAULT NOW()
);

-- Optional: basic index for faster lookups by location and company
CREATE INDEX IF NOT EXISTS idx_jobs_location ON jobs (location);
CREATE INDEX IF NOT EXISTS idx_jobs_company ON jobs (company);

