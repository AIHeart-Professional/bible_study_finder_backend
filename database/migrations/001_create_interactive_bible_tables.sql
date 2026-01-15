-- Migration: Create Interactive Bible Tables
-- Description: Creates tables for interactive bible map feature
-- Tables: events, locations, movements, speakers

-- Create events table
CREATE TABLE IF NOT EXISTS events (
	id SERIAL PRIMARY KEY,
	verse_id TEXT NOT NULL,
	image_url TEXT,
	title TEXT
);

-- Create locations table
CREATE TABLE IF NOT EXISTS locations (
	id SERIAL PRIMARY KEY,
	verse_id TEXT NOT NULL,
	place TEXT NOT NULL,
	latitude REAL NOT NULL,
	longitude REAL NOT NULL,
	confidence INTEGER
);

-- Create movements table
CREATE TABLE IF NOT EXISTS movements (
	id SERIAL PRIMARY KEY,
	verse_id TEXT NOT NULL,
	actor TEXT,
	from_place TEXT,
	from_lat REAL,
	from_lng REAL,
	to_place TEXT,
	to_lat REAL,
	to_lng REAL,
	duration_ms INTEGER
);

-- Create speakers table
CREATE TABLE IF NOT EXISTS speakers (
	id SERIAL PRIMARY KEY,
	name TEXT NOT NULL,
	icon_asset TEXT,
	color TEXT
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_locations_verse_id ON locations(verse_id);
CREATE INDEX IF NOT EXISTS idx_locations_place ON locations(place);
CREATE INDEX IF NOT EXISTS idx_events_verse_id ON events(verse_id);
CREATE INDEX IF NOT EXISTS idx_movements_verse_id ON movements(verse_id);

