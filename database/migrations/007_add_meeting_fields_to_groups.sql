-- Migration: Add new fields to groups table
-- Description: Adds meeting_consistency, status, meeting_days, meeting_start_time, and meeting_end_time columns

-- Add meeting_consistency column
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'groups' AND column_name = 'meeting_consistency'
    ) THEN
        ALTER TABLE groups ADD COLUMN meeting_consistency TEXT;
        RAISE NOTICE 'Added meeting_consistency column to groups table';
    ELSE
        RAISE NOTICE 'meeting_consistency column already exists in groups table';
    END IF;
END $$;

-- Add status column
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'groups' AND column_name = 'status'
    ) THEN
        ALTER TABLE groups ADD COLUMN status TEXT;
        RAISE NOTICE 'Added status column to groups table';
    ELSE
        RAISE NOTICE 'status column already exists in groups table';
    END IF;
END $$;

-- Add meeting_days column
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'groups' AND column_name = 'meeting_days'
    ) THEN
        ALTER TABLE groups ADD COLUMN meeting_days JSONB DEFAULT '[]'::jsonb;
        RAISE NOTICE 'Added meeting_days column to groups table';
    ELSE
        RAISE NOTICE 'meeting_days column already exists in groups table';
    END IF;
END $$;

-- Add meeting_start_time column
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'groups' AND column_name = 'meeting_start_time'
    ) THEN
        ALTER TABLE groups ADD COLUMN meeting_start_time TIMESTAMP WITH TIME ZONE;
        RAISE NOTICE 'Added meeting_start_time column to groups table';
    ELSE
        RAISE NOTICE 'meeting_start_time column already exists in groups table';
    END IF;
END $$;

-- Add meeting_end_time column
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'groups' AND column_name = 'meeting_end_time'
    ) THEN
        ALTER TABLE groups ADD COLUMN meeting_end_time TIMESTAMP WITH TIME ZONE;
        RAISE NOTICE 'Added meeting_end_time column to groups table';
    ELSE
        RAISE NOTICE 'meeting_end_time column already exists in groups table';
    END IF;
END $$;

