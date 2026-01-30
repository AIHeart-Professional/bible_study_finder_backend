"""Interactive Bible routes - HTTP layer."""
from typing import List
from fastapi import APIRouter, Query
from src.models.interactive_bible import LocationResponse, ChapterLocationResponse, ChapterCharacterResponse, VerseCharacterResponse
from src.controller.interactive_bible.locations_controller import LocationsController

# Create a router for Interactive Bible-related routes
router = APIRouter()

@router.get("/locations", response_model=List[LocationResponse])
async def get_locations():
	"""
	Get all locations for the interactive bible map.
	
	Returns:
		List of LocationResponse objects with id, name, lat, lng, and verses
	"""
	results = await LocationsController().get_locations()
	return results

@router.get("/get_locations_from_chapter", response_model=List[ChapterLocationResponse])
async def get_locations_from_chapter(
	book: str = Query(..., description="Book name (e.g., 'Mark')"),
	chapter: int = Query(..., description="Chapter number")
):
	"""
	Get locations from a specific chapter, ranked by confidence.
	Returns only the highest confidence location for each verse.
	
	Query Parameters:
		book: Book name (e.g., 'Mark')
		chapter: Chapter number
	
	Returns:
		List of ChapterLocationResponse objects with book, chapter, verse, name, longitude, latitude
	"""
	results = await LocationsController().get_locations_from_chapter(book, chapter)
	return results

@router.get("/get_bible_characters_from_chapter", response_model=List[ChapterCharacterResponse])
async def get_bible_characters_from_chapter(
	book: str = Query(..., description="Book name (e.g., 'Mark')"),
	chapter: int = Query(..., description="Chapter number")
):
	"""
	Get all character names from a specific chapter.
	Finds characters by matching book and chapter in verse_characters table.
	Also joins with verse_dialogue to include textbox field when available.
	
	Query Parameters:
		book: Book name (e.g., 'Mark')
		chapter: Chapter number
	
	Returns:
		List of ChapterCharacterResponse objects with name, book, chapter, verse, 
		longitude, latitude, appear_offset_ms, travel_duration_ms, ease, textbox (optional)
	"""
	results = await LocationsController().get_characters_from_chapter(book, chapter)
	return results

@router.get("/get_bible_characters_from_verse", response_model=List[VerseCharacterResponse])
async def get_bible_characters_from_verse(
	book: str = Query(..., description="Book name (e.g., 'Mark')"),
	chapter: int = Query(..., description="Chapter number"),
	verse: int = Query(..., description="Verse number")
):
	"""
	Get all character names from a specific verse.
	Finds characters by matching exact book, chapter, and verse in verse_characters table.
	Also joins with verse_dialogue to include textbox field when available.
	
	Query Parameters:
		book: Book name (e.g., 'Mark')
		chapter: Chapter number
		verse: Verse number
	
	Returns:
		List of VerseCharacterResponse objects with name, book, chapter, verse, 
		longitude, latitude, appear_offset_ms, travel_duration_ms, ease, textbox (optional)
	"""
	results = await LocationsController().get_characters_from_verse(book, chapter, verse)
	return results

