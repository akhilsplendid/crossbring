-- Crossbring JobModel DDL (PostgreSQL)
CREATE SCHEMA IF NOT EXISTS jobmodel;

-- Dimensions
CREATE TABLE IF NOT EXISTS jobmodel.dim_employer (
    employer_id SERIAL PRIMARY KEY,
    employer_name TEXT NOT NULL UNIQUE,
    website TEXT,
    created_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE IF NOT EXISTS jobmodel.dim_location (
    location_id SERIAL PRIMARY KEY,
    country_code TEXT NOT NULL DEFAULT 'SE',
    region TEXT,
    city TEXT,
    UNIQUE (country_code, region, city)
);

CREATE TABLE IF NOT EXISTS jobmodel.dim_technology (
    tech_id SERIAL PRIMARY KEY,
    tech_name TEXT NOT NULL UNIQUE
);

-- Posting fact (SCD2-style)
CREATE TABLE IF NOT EXISTS jobmodel.fact_posting (
    posting_sk BIGSERIAL PRIMARY KEY,
    job_id TEXT NOT NULL,
    title TEXT NOT NULL,
    description TEXT,
    language TEXT,
    employer_id INT REFERENCES jobmodel.dim_employer(employer_id),
    location_id INT REFERENCES jobmodel.dim_location(location_id),
    tech_ids INT[] DEFAULT '{}',
    source TEXT,
    valid_from TIMESTAMPTZ NOT NULL DEFAULT now(),
    valid_to   TIMESTAMPTZ,
    is_current BOOLEAN GENERATED ALWAYS AS (valid_to IS NULL) STORED
);

CREATE INDEX IF NOT EXISTS idx_fact_posting_job_id ON jobmodel.fact_posting(job_id);
CREATE INDEX IF NOT EXISTS idx_fact_posting_current ON jobmodel.fact_posting(is_current);

-- Staging tables (optional) populated by transformers/CDC
CREATE TABLE IF NOT EXISTS jobmodel.stg_jobs (
    job_id TEXT PRIMARY KEY,
    title TEXT,
    description TEXT,
    employer_name TEXT,
    city TEXT,
    region TEXT,
    country_code TEXT,
    language TEXT,
    tech_tags TEXT[],
    source TEXT,
    updated_at TIMESTAMPTZ DEFAULT now()
);

