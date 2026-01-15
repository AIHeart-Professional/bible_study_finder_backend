"""Locations database - Data access layer for PostgreSQL."""
from typing import List, Optional
from src.utils.logger import get_logger
from src.utils.postgres_connection import PostgresConnection

class LocationsDatabase:
	"""Database layer for location operations."""
	
	def __init__(self):
		"""Initialize the database connection."""
		self.logger = get_logger(__name__)
		self.logger.info("LocationsDatabase initialized successfully")
	
	async def get_all_locations(self) -> List[dict]:
		"""
		Get all locations grouped by place name with aggregated verse_ids.
		
		Returns:
			List of location dictionaries with id, name, lat, lng, verses
		"""
		self.logger.debug("get_all_locations called")
		
		connection = None
		try:
			connection = PostgresConnection.get_connection()
			cursor = connection.cursor()
			
			self.logger.debug("Executing SQL query to get all locations")
			
			query = """
				SELECT 
					name AS name,
					latitude AS lat,
					longitude AS lng,
					ARRAY_AGG(DISTINCT verse_id) AS verses
				FROM bible_locations
				WHERE name IS NOT NULL
					AND latitude IS NOT NULL
					AND longitude IS NOT NULL
				GROUP BY name, latitude, longitude
				ORDER BY name
			"""
			
			cursor.execute(query)
			results = cursor.fetchall()
			
			self.logger.debug(f"Query returned {len(results)} location groups")
			
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
			
		finally:
			if connection:
				PostgresConnection.return_connection(connection)
				self.logger.debug("Connection returned to pool")
	
	async def get_locations_from_chapter(self, book: str, chapter: int) -> List[dict]:
		"""
		Get locations from a specific chapter, ranked by confidence.
		Returns only rank #1 (highest confidence) location for each verse.
		
		Args:
			book: Book name (e.g., 'Mark')
			chapter: Chapter number
		
		Returns:
			List of location dictionaries with book, chapter, verse, name, longitude, latitude
		"""
		self.logger.debug(f"get_locations_from_chapter called with book={book}, chapter={chapter}")
		
		connection = None
		try:
			connection = PostgresConnection.get_connection()
			cursor = connection.cursor()
			
			self.logger.debug("Executing SQL query to get locations from chapter")
			
			query = """
				WITH ranked_locations AS (
					SELECT 
						verse_id,
						verse,
						name,
						latitude,
						longitude,
						confidence,
						ROW_NUMBER() OVER (PARTITION BY verse ORDER BY confidence DESC) as rank
					FROM bible_locations
					WHERE book = %s AND chapter = %s
				)
				SELECT 
					verse_id,
					verse,
					name,
					latitude,
					longitude,
					confidence
				FROM ranked_locations
				WHERE rank = 1
				ORDER BY verse
			"""
			
			cursor.execute(query, (book, chapter))
			results = cursor.fetchall()
			
			self.logger.debug(f"Query returned {len(results)} locations")
			
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
			
		finally:
			if connection:
				PostgresConnection.return_connection(connection)
				self.logger.debug("Connection returned to pool")
	
	async def get_characters_from_chapter(self, book: str, chapter: int) -> List[dict]:
		"""
		Get all character names from a specific chapter.
		Finds characters by matching verse_id pattern (book.chapter.verse) in verse_characters table.
		
		Args:
			book: Book name (e.g., 'Mark')
			chapter: Chapter number
		
		Returns:
			List of character dictionaries with name
		"""
		self.logger.debug(f"get_characters_from_chapter called with book={book}, chapter={chapter}")
		
		connection = None
		try:
			connection = PostgresConnection.get_connection()
			cursor = connection.cursor()
			
			self.logger.debug("Executing SQL query to get characters from chapter")
			
			# Build verse_id pattern: "Mark.1.%"
			verse_pattern = f"{book}.{chapter}.%"
			
			query = """
				SELECT DISTINCT bc.name
				FROM verse_characters vc
				JOIN bible_characters bc ON vc.character_id = bc.id
				WHERE vc.verse_id LIKE %s
				ORDER BY bc.name
			"""
			
			cursor.execute(query, (verse_pattern,))
			results = cursor.fetchall()
			
			self.logger.debug(f"Query returned {len(results)} characters")
			
			characters = []
			for row in results:
				character = {
					'name': row['name']
				}
				characters.append(character)
			
			self.logger.info(f"Successfully retrieved {len(characters)} characters from {book} chapter {chapter}")
			return characters
			
		except Exception as e:
			self.logger.error(f"Error getting characters from chapter: {e}", exc_info=True)
			return []
			
		finally:
			if connection:
				PostgresConnection.return_connection(connection)
				self.logger.debug("Connection returned to pool")
	
	async def get_characters_from_verse(self, book: str, chapter: int, verse: int) -> List[dict]:
		"""
		Get all character names from a specific verse.
		Finds characters by matching exact verse_id (book.chapter.verse) in verse_characters table.
		
		Args:
			book: Book name (e.g., 'Mark')
			chapter: Chapter number
			verse: Verse number
		
		Returns:
			List of character dictionaries with book, chapter, verse, name
		"""
		self.logger.debug(f"get_characters_from_verse called with book={book}, chapter={chapter}, verse={verse}")
		
		connection = None
		try:
			connection = PostgresConnection.get_connection()
			cursor = connection.cursor()
			
			self.logger.debug("Executing SQL query to get characters from verse")
			
			# Build exact verse_id: "Mark.1.21"
			verse_id = f"{book}.{chapter}.{verse}"
			
			query = """
				SELECT DISTINCT bc.name
				FROM verse_characters vc
				JOIN bible_characters bc ON vc.character_id = bc.id
				WHERE vc.verse_id = %s
				ORDER BY bc.name
			"""
			
			cursor.execute(query, (verse_id,))
			results = cursor.fetchall()
			
			self.logger.debug(f"Query returned {len(results)} characters")
			
			characters = []
			for row in results:
				character = {
					'book': book,
					'chapter': chapter,
					'verse': verse,
					'name': row['name']
				}
				characters.append(character)
			
			self.logger.info(f"Successfully retrieved {len(characters)} characters from {book} {chapter}:{verse}")
			return characters
			
		except Exception as e:
			self.logger.error(f"Error getting characters from verse: {e}", exc_info=True)
			return []
			
		finally:
			if connection:
				PostgresConnection.return_connection(connection)
				self.logger.debug("Connection returned to pool")

