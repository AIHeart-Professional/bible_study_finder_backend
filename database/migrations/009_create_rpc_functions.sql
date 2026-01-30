-- Migration: Create RPC functions for Supabase HTTP API
-- These functions allow complex queries to be called via Supabase REST API

-- Function: Get all locations with confidence >= 400
CREATE OR REPLACE FUNCTION get_all_locations()
RETURNS TABLE (
    name TEXT,
    lat DOUBLE PRECISION,
    lng DOUBLE PRECISION,
    verses TEXT[]
) 
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
BEGIN
    RETURN QUERY
    SELECT 
        bl.name::TEXT,
        bl.latitude::DOUBLE PRECISION AS lat,
        bl.longitude::DOUBLE PRECISION AS lng,
        ARRAY_AGG(DISTINCT bl.verse_id)::TEXT[] AS verses
    FROM bible_locations bl
    WHERE bl.name IS NOT NULL
        AND bl.latitude IS NOT NULL
        AND bl.longitude IS NOT NULL
        AND bl.confidence >= 400
    GROUP BY bl.name, bl.latitude, bl.longitude
    ORDER BY bl.name;
END;
$$;

-- Function: Get locations from a specific chapter
CREATE OR REPLACE FUNCTION get_locations_from_chapter(
    p_book TEXT,
    p_chapter INTEGER
)
RETURNS TABLE (
    verse_id TEXT,
    verse INTEGER,
    name TEXT,
    latitude DOUBLE PRECISION,
    longitude DOUBLE PRECISION,
    confidence INTEGER
)
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
BEGIN
    RETURN QUERY
    WITH ranked_locations AS (
        SELECT 
            bl.verse_id,
            bl.verse,
            bl.name,
            bl.latitude,
            bl.longitude,
            bl.confidence,
            ROW_NUMBER() OVER (PARTITION BY bl.verse ORDER BY bl.confidence DESC) as rank
        FROM bible_locations bl
        WHERE bl.book = p_book 
            AND bl.chapter = p_chapter 
            AND bl.confidence >= 400
    )
    SELECT 
        rl.verse_id::TEXT,
        rl.verse::INTEGER,
        rl.name::TEXT,
        rl.latitude::DOUBLE PRECISION,
        rl.longitude::DOUBLE PRECISION,
        rl.confidence::INTEGER
    FROM ranked_locations rl
    WHERE rl.rank = 1
    ORDER BY rl.verse;
END;
$$;

-- Function: Get characters from a specific chapter with dialog info
CREATE OR REPLACE FUNCTION get_characters_from_chapter(
    p_book TEXT,
    p_chapter INTEGER
)
RETURNS TABLE (
    name TEXT,
    book TEXT,
    chapter INTEGER,
    verse INTEGER,
    longitude DOUBLE PRECISION,
    latitude DOUBLE PRECISION,
    appear_offset_ms INTEGER,
    travel_duration_ms INTEGER,
    ease TEXT,
    textbox TEXT
)
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
BEGIN
    RETURN QUERY
    SELECT 
        bc.name::TEXT,
        vc.book::TEXT,
        vc.chapter::INTEGER,
        vc.verse::INTEGER,
        COALESCE(vc.longitude, 0.0)::DOUBLE PRECISION,
        COALESCE(vc.latitude, 0.0)::DOUBLE PRECISION,
        COALESCE(vc.appear_offset_ms, 0)::INTEGER,
        COALESCE(vc.travel_duration_ms, 800)::INTEGER,
        COALESCE(vc.ease::TEXT, 'ease-out')::TEXT,
        vd.textbox::TEXT
    FROM verse_characters vc
    JOIN bible_characters bc ON vc.character_id = bc.id
    LEFT JOIN verse_dialogue vd ON 
        vd.book = vc.book AND 
        vd.chapter = vc.chapter AND 
        vd.verse = vc.verse AND 
        vd.character_id = vc.character_id
    WHERE vc.book = p_book AND vc.chapter = p_chapter
    ORDER BY vc.verse, vd.display_order, bc.name;
END;
$$;

-- Function: Get characters from a specific verse with dialog info
CREATE OR REPLACE FUNCTION get_characters_from_verse(
    p_book TEXT,
    p_chapter INTEGER,
    p_verse INTEGER
)
RETURNS TABLE (
    name TEXT,
    book TEXT,
    chapter INTEGER,
    verse INTEGER,
    longitude DOUBLE PRECISION,
    latitude DOUBLE PRECISION,
    appear_offset_ms INTEGER,
    travel_duration_ms INTEGER,
    ease TEXT,
    textbox TEXT
)
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
BEGIN
    RETURN QUERY
    SELECT 
        bc.name::TEXT,
        vc.book::TEXT,
        vc.chapter::INTEGER,
        vc.verse::INTEGER,
        COALESCE(vc.longitude, 0.0)::DOUBLE PRECISION,
        COALESCE(vc.latitude, 0.0)::DOUBLE PRECISION,
        COALESCE(vc.appear_offset_ms, 0)::INTEGER,
        COALESCE(vc.travel_duration_ms, 800)::INTEGER,
        COALESCE(vc.ease::TEXT, 'ease-out')::TEXT,
        vd.textbox::TEXT
    FROM verse_characters vc
    JOIN bible_characters bc ON vc.character_id = bc.id
    LEFT JOIN verse_dialogue vd ON 
        vd.book = vc.book AND 
        vd.chapter = vc.chapter AND 
        vd.verse = vc.verse AND 
        vd.character_id = vc.character_id
    WHERE vc.book = p_book AND vc.chapter = p_chapter AND vc.verse = p_verse
    ORDER BY vd.display_order, bc.name;
END;
$$;

-- Grant execute permissions to authenticated and anon roles
GRANT EXECUTE ON FUNCTION get_all_locations() TO authenticated, anon;
GRANT EXECUTE ON FUNCTION get_locations_from_chapter(TEXT, INTEGER) TO authenticated, anon;
GRANT EXECUTE ON FUNCTION get_characters_from_chapter(TEXT, INTEGER) TO authenticated, anon;
GRANT EXECUTE ON FUNCTION get_characters_from_verse(TEXT, INTEGER, INTEGER) TO authenticated, anon;

-- Add comments for documentation
COMMENT ON FUNCTION get_all_locations() IS 'Get all locations with confidence >= 400, grouped by place name';
COMMENT ON FUNCTION get_locations_from_chapter(TEXT, INTEGER) IS 'Get highest confidence location for each verse in a chapter';
COMMENT ON FUNCTION get_characters_from_chapter(TEXT, INTEGER) IS 'Get all characters from a chapter with dialog info';
COMMENT ON FUNCTION get_characters_from_verse(TEXT, INTEGER, INTEGER) IS 'Get all characters from a specific verse with dialog info';
