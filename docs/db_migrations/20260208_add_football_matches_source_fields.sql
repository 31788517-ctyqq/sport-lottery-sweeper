-- Add minimal fields to store full 100qiu raw payload.
-- Choose the variant that matches your database engine.

-- MySQL / MariaDB
ALTER TABLE football_matches ADD COLUMN data_source VARCHAR(50) DEFAULT '100qiu';
ALTER TABLE football_matches ADD COLUMN source_attributes JSON NULL;

-- PostgreSQL
-- ALTER TABLE football_matches ADD COLUMN data_source VARCHAR(50) DEFAULT '100qiu';
-- ALTER TABLE football_matches ADD COLUMN source_attributes JSONB;

-- SQLite (JSON stored as TEXT)
-- ALTER TABLE football_matches ADD COLUMN data_source TEXT DEFAULT '100qiu';
-- ALTER TABLE football_matches ADD COLUMN source_attributes TEXT;
