"""Locations service - Application logic layer."""
from typing import List
from src.utils.logger import get_logger
from src.database.interactive_bible.locations_database import LocationsDatabase

class LocationsService:
	"""Service for handling location business logic."""
	
	def __init__(self):
		"""Initialize the service and database."""
		self.logger = get_logger(__name__)
		self.locations_database = LocationsDatabase()
		self.logger.info("LocationsService initialized successfully")
	
	async def get_locations(self) -> List[dict]:
		"""
		Get all locations.
		
		Returns:
			List of location dictionaries
		"""
		self.logger.debug("get_locations called")
		
		try:
			locations = await self.locations_database.get_all_locations()
			
			self.logger.info(f"Successfully retrieved {len(locations)} locations")
			return locations
			
		except Exception as e:
			self.logger.error(f"Error getting locations: {e}", exc_info=True)
			return []
	
	async def get_locations_from_chapter(self, book: str, chapter: int) -> List[dict]:
		"""
		Get locations from a specific chapter.
		
		Args:
			book: Book name (e.g., 'Mark')
			chapter: Chapter number
		
		Returns:
			List of location dictionaries
		"""
		self.logger.debug(f"get_locations_from_chapter called with book={book}, chapter={chapter}")
		
		try:
			locations = await self.locations_database.get_locations_from_chapter(book, chapter)
			
			self.logger.info(f"Successfully retrieved {len(locations)} locations from {book} chapter {chapter}")
			return locations
			
		except Exception as e:
			self.logger.error(f"Error getting locations from chapter: {e}", exc_info=True)
			return []
	
	async def get_characters_from_chapter(self, book: str, chapter: int) -> List[dict]:
		"""
		Get character names from a specific chapter.
		
		Args:
			book: Book name (e.g., 'Mark')
			chapter: Chapter number
		
		Returns:
			List of character dictionaries with name, book, chapter, verse, longitude, latitude
		"""
		self.logger.debug(f"get_characters_from_chapter called with book={book}, chapter={chapter}")
		
		try:
			characters = await self.locations_database.get_characters_from_chapter(book, chapter)
			
			self.logger.info(f"Successfully retrieved {len(characters)} characters from {book} chapter {chapter}")
			return characters
			
		except Exception as e:
			self.logger.error(f"Error getting characters from chapter: {e}", exc_info=True)
			return []
	
	async def get_characters_from_verse(self, book: str, chapter: int, verse: int) -> List[dict]:
		"""
		Get character names from a specific verse.
		
		Args:
			book: Book name (e.g., 'Mark')
			chapter: Chapter number
			verse: Verse number
		
		Returns:
			List of character dictionaries with name, book, chapter, verse, longitude, latitude
		"""
		self.logger.debug(f"get_characters_from_verse called with book={book}, chapter={chapter}, verse={verse}")
		
		try:
			characters = await self.locations_database.get_characters_from_verse(book, chapter, verse)
			
			self.logger.info(f"Successfully retrieved {len(characters)} characters from {book} {chapter}:{verse}")
			return characters
			
		except Exception as e:
			self.logger.error(f"Error getting characters from verse: {e}", exc_info=True)
			return []

