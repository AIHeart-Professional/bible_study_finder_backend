-- Migration: Add animation timing fields to verse_characters table
-- These fields allow per-character control over map icon animations
--
-- Fields:
--   appear_offset_ms: Delay before icon appears relative to verse start (0 = immediate)
--   travel_duration_ms: Duration of movement animation between positions (default 800ms)
--   easing_hint: Animation easing style ('ease-out', 'linear', 'ease-in-out', 'snap')

ALTER TABLE verse_characters
ADD COLUMN IF NOT EXISTS appear_offset_ms INTEGER DEFAULT 0,
ADD COLUMN IF NOT EXISTS travel_duration_ms INTEGER DEFAULT 800,
ADD COLUMN IF NOT EXISTS easing_hint VARCHAR(50) DEFAULT 'ease-out';

-- Add comments for documentation
COMMENT ON COLUMN verse_characters.appear_offset_ms IS 'Delay in ms before character icon appears when entering this verse (0 = immediate)';
COMMENT ON COLUMN verse_characters.travel_duration_ms IS 'Duration in ms for movement animation from previous position (default 800)';
COMMENT ON COLUMN verse_characters.easing_hint IS 'Animation easing style: ease-out, linear, ease-in-out, snap (default ease-out)';

-- Create index for potential filtering by animation properties
CREATE INDEX IF NOT EXISTS idx_verse_characters_animation 
ON verse_characters (appear_offset_ms, travel_duration_ms);
