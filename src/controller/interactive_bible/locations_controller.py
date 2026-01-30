"""Locations controller - Business logic distributor layer."""
from typing import List
from src.models.interactive_bible import LocationResponse, ChapterLocationResponse, ChapterCharacterResponse, VerseCharacterResponse
from src.utils.logger import get_logger
from src.services.locations_service import LocationsService

class LocationsController:
	"""Controller for handling location business logic."""
	
	def __init__(self):
		"""Initialize the controller and locations service."""
		self.locations_service = LocationsService()
		self.logger = get_logger(__name__)
		self.logger.info("LocationsController initialized successfully")
	
	async def get_locations(self) -> List[LocationResponse]:
		"""
		Get all locations.
		
		Returns:
			List of LocationResponse objects
		"""
		self.logger.debug("get_locations called")
		
		try:
			locations_data = await self.locations_service.get_locations()
			
			locations = [
				LocationResponse(
					id=loc['id'],
					name=loc['name'],
					lat=loc['lat'],
					lng=loc['lng'],
					verses=loc['verses']
				)
				for loc in locations_data
			]
			
			self.logger.info(f"Successfully converted {len(locations)} locations to response models")
			return locations
			
		except Exception as e:
			self.logger.error(f"Error getting locations: {e}", exc_info=True)
			return []
	
	async def get_locations_from_chapter(self, book: str, chapter: int) -> List[ChapterLocationResponse]:
		"""
		Get locations from a specific chapter.
		
		Args:
			book: Book name (e.g., 'Mark')
			chapter: Chapter number
		
		Returns:
			List of ChapterLocationResponse objects
		"""
		self.logger.debug(f"get_locations_from_chapter called with book={book}, chapter={chapter}")
		
		try:
			locations_data = await self.locations_service.get_locations_from_chapter(book, chapter)
			
			locations = [
				ChapterLocationResponse(
					book=loc['book'],
					chapter=loc['chapter'],
					verse=loc['verse'],
					name=loc['name'],
					longitude=loc['longitude'],
					latitude=loc['latitude']
				)
				for loc in locations_data
			]
			
			self.logger.info(f"Successfully converted {len(locations)} chapter locations to response models")
			return locations
			
		except Exception as e:
			self.logger.error(f"Error getting locations from chapter: {e}", exc_info=True)
			return []
	
	async def get_characters_from_chapter(self, book: str, chapter: int) -> List[ChapterCharacterResponse]:
		"""
		Get character names from a specific chapter.
		
		Args:
			book: Book name (e.g., 'Mark')
			chapter: Chapter number
		
		Returns:
			List of ChapterCharacterResponse objects with name, book, chapter, verse,
			longitude, latitude, appear_offset_ms, travel_duration_ms, ease, textbox
		"""
		self.logger.debug(f"get_characters_from_chapter called with book={book}, chapter={chapter}")
		
		try:
			characters_data = await self.locations_service.get_characters_from_chapter(book, chapter)
			
			characters = [
				self._build_chapter_character_response(char)
				for char in characters_data
			]
			
			self.logger.info(f"Successfully converted {len(characters)} characters to response models")
			return characters
			
		except Exception as e:
			self.logger.error(f"Error getting characters from chapter: {e}", exc_info=True)
			return []
	
	def _build_chapter_character_response(self, char: dict) -> ChapterCharacterResponse:
		"""
		Build a ChapterCharacterResponse from character data.
		
		Args:
			char: Character dictionary from service layer
		
		Returns:
			ChapterCharacterResponse object
		"""
		return ChapterCharacterResponse(
			name=char['name'],
			book=char['book'],
			chapter=char['chapter'],
			verse=char['verse'],
			longitude=char['longitude'],
			latitude=char['latitude'],
			appear_offset_ms=char['appear_offset_ms'],
			travel_duration_ms=char['travel_duration_ms'],
			ease=char['ease'],
			textbox=char.get('textbox')
		)
	
	async def get_characters_from_verse(self, book: str, chapter: int, verse: int) -> List[VerseCharacterResponse]:
		"""
		Get character names from a specific verse.
		
		Args:
			book: Book name (e.g., 'Mark')
			chapter: Chapter number
			verse: Verse number
		
		Returns:
			List of VerseCharacterResponse objects with name, book, chapter, verse,
			longitude, latitude, appear_offset_ms, travel_duration_ms, ease, textbox
		"""
		self.logger.debug(f"get_characters_from_verse called with book={book}, chapter={chapter}, verse={verse}")
		
		try:
			characters_data = await self.locations_service.get_characters_from_verse(book, chapter, verse)
			
			characters = [
				self._build_verse_character_response(char)
				for char in characters_data
			]
			
			self.logger.info(f"Successfully converted {len(characters)} verse characters to response models")
			return characters
			
		except Exception as e:
			self.logger.error(f"Error getting characters from verse: {e}", exc_info=True)
			return []
	
	def _build_verse_character_response(self, char: dict) -> VerseCharacterResponse:
		"""
		Build a VerseCharacterResponse from character data.
		
		Args:
			char: Character dictionary from service layer
		
		Returns:
			VerseCharacterResponse object
		"""
		return VerseCharacterResponse(
			name=char['name'],
			book=char['book'],
			chapter=char['chapter'],
			verse=char['verse'],
			longitude=char['longitude'],
			latitude=char['latitude'],
			appear_offset_ms=char['appear_offset_ms'],
			travel_duration_ms=char['travel_duration_ms'],
			ease=char['ease'],
			textbox=char.get('textbox')
		)

