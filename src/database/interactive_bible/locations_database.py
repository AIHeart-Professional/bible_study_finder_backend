"""Locations database - Data access layer using Supabase HTTP API."""
from typing import List
from src.utils.logger import get_logger
from src.utils.supabase_client import SupabaseClient


class LocationsDatabase:
    """Database layer for location operations using Supabase HTTP API."""
    
    def __init__(self):
        """Initialize the database connection."""
        self.logger = get_logger(__name__)
        self.client = SupabaseClient.get_instance()
        self.logger.info("LocationsDatabase initialized successfully")
    
    async def get_all_locations(self) -> List[dict]:
        """
        Get all locations grouped by place name with aggregated verse_ids.
        Only includes locations with confidence >= 400.
        Uses Supabase RPC function.
        
        Returns:
            List of location dictionaries with id, name, lat, lng, verses
        """
        self.logger.debug("get_all_locations called")
        
        try:
            results = await self.client.rpc("get_all_locations")
            
            self.logger.debug(f"RPC returned {len(results)} location groups")
            
            locations = []
            for idx, row in enumerate(results):
                location = {
                    'id': f"location-{idx + 1}",
                    'name': row['name'],
                    'lat': float(row['lat']),
                    'lng': float(row['lng']),
                    'verses': row['verses'] if row['verses'] else []
                }
                locations.append(location)
            
            self.logger.info(f"Successfully retrieved {len(locations)} locations")
            return locations
            
        except Exception as e:
            self.logger.error(f"Error getting all locations: {e}", exc_info=True)
            return []
    
    async def get_locations_from_chapter(self, book: str, chapter: int) -> List[dict]:
        """
        Get locations from a specific chapter, ranked by confidence.
        Returns only rank #1 (highest confidence) location for each verse.
        Only includes locations with confidence >= 400.
        Uses Supabase RPC function.
        
        Args:
            book: Book name (e.g., 'Mark')
            chapter: Chapter number
        
        Returns:
            List of location dictionaries with book, chapter, verse, name, longitude, latitude
        """
        self.logger.debug(f"get_locations_from_chapter called with book={book}, chapter={chapter}")
        
        try:
            results = await self.client.rpc(
                "get_locations_from_chapter",
                {"p_book": book, "p_chapter": chapter}
            )
            
            self.logger.debug(f"RPC returned {len(results)} locations")
            
            locations = []
            for row in results:
                location = {
                    'book': book,
                    'chapter': chapter,
                    'verse': int(row['verse']),
                    'name': row['name'],
                    'longitude': float(row['longitude']),
                    'latitude': float(row['latitude'])
                }
                locations.append(location)
            
            self.logger.info(f"Successfully retrieved {len(locations)} locations from {book} chapter {chapter}")
            return locations
            
        except Exception as e:
            self.logger.error(f"Error getting locations from chapter: {e}", exc_info=True)
            return []
    
    async def get_characters_from_chapter(self, book: str, chapter: int) -> List[dict]:
        """
        Get all character names from a specific chapter.
        Finds characters by matching book and chapter in verse_characters table.
        Also joins with verse_dialogue to get textbox field if available.
        Uses Supabase RPC function.
        
        Args:
            book: Book name (e.g., 'Mark')
            chapter: Chapter number
        
        Returns:
            List of character dictionaries with name, book, chapter, verse, 
            longitude, latitude, animation fields, and optional textbox
        """
        self.logger.debug(f"get_characters_from_chapter called with book={book}, chapter={chapter}")
        
        try:
            results = await self.client.rpc(
                "get_characters_from_chapter",
                {"p_book": book, "p_chapter": chapter}
            )
            
            self.logger.debug(f"RPC returned {len(results)} characters")
            
            characters = self._format_character_rows(results)
            
            self.logger.info(f"Successfully retrieved {len(characters)} characters from {book} chapter {chapter}")
            return characters
            
        except Exception as e:
            self.logger.error(f"Error getting characters from chapter: {e}", exc_info=True)
            return []
    
    def _format_character_rows(self, results: List[dict]) -> List[dict]:
        """
        Format character result rows into dictionaries.
        
        Args:
            results: List of database row results
        
        Returns:
            List of formatted character dictionaries
        """
        characters = []
        for row in results:
            character = self._format_single_character(row)
            characters.append(character)
        return characters
    
    def _format_single_character(self, row: dict) -> dict:
        """
        Format a single character row into a dictionary.
        
        Args:
            row: Database row result
        
        Returns:
            Formatted character dictionary
        """
        character = {
            'name': row['name'],
            'book': row['book'],
            'chapter': int(row['chapter']),
            'verse': int(row['verse']),
            'longitude': float(row['longitude']) if row['longitude'] is not None else 0.0,
            'latitude': float(row['latitude']) if row['latitude'] is not None else 0.0,
            'appear_offset_ms': int(row['appear_offset_ms']) if row['appear_offset_ms'] is not None else 0,
            'travel_duration_ms': int(row['travel_duration_ms']) if row['travel_duration_ms'] is not None else 800,
            'ease': row['ease'] if row['ease'] is not None else 'ease-out'
        }
        
        # Only include textbox if it exists in the verse_dialogue table
        if row.get('textbox') is not None:
            character['textbox'] = row['textbox']
        
        return character
    
    async def get_characters_from_verse(self, book: str, chapter: int, verse: int) -> List[dict]:
        """
        Get all character names from a specific verse.
        Finds characters by matching exact book, chapter, and verse in verse_characters table.
        Also joins with verse_dialogue to get textbox field if available.
        Uses Supabase RPC function.
        
        Args:
            book: Book name (e.g., 'Mark')
            chapter: Chapter number
            verse: Verse number
        
        Returns:
            List of character dictionaries with name, book, chapter, verse, 
            longitude, latitude, animation fields, and optional textbox
        """
        self.logger.debug(f"get_characters_from_verse called with book={book}, chapter={chapter}, verse={verse}")
        
        try:
            results = await self.client.rpc(
                "get_characters_from_verse",
                {"p_book": book, "p_chapter": chapter, "p_verse": verse}
            )
            
            self.logger.debug(f"RPC returned {len(results)} characters")
            
            characters = self._format_character_rows(results)
            
            self.logger.info(f"Successfully retrieved {len(characters)} characters from {book} {chapter}:{verse}")
            return characters
            
        except Exception as e:
            self.logger.error(f"Error getting characters from verse: {e}", exc_info=True)
            return []
