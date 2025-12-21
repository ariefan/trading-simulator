-- Initialize TimescaleDB and create base tables
-- This runs automatically when the PostgreSQL container starts

-- Enable TimescaleDB extension
CREATE EXTENSION IF NOT EXISTS timescaledb;

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Note: The actual tables are created by Alembic migrations
-- This file just ensures extensions are loaded

-- Log successful initialization
DO $$
BEGIN
    RAISE NOTICE 'Database initialized with TimescaleDB extension';
END $$;
