"""
Format and normalize Bible reference strings.

Example: "Mark 1:3-5; John 3:5, Mark: 7" -> "Mark 1:3–5, 7; 1 John 3:5"
Groups by book (including numbered books like 1 John), then by chapter, then verse ranges.
Uses en-dash (–) for ranges.
"""
import re
from typing import List, Tuple, Dict, Optional
from collections import defaultdict

# En-dash for verse ranges
EN_DASH = "\u2013"


def _parse_single_ref(text: str) -> Optional[Tuple[str, Optional[int], Optional[int], Optional[int]]]:
    """
    Parse one reference piece into (book, chapter, verse_start, verse_end).
    Examples: "Mark 1:3-5" -> ("Mark", 1, 3, 5); "Mark: 7" -> ("Mark", None, 7, 7); "John 3:5" -> ("John", 3, 5, 5).
    """
    text = text.strip()
    if not text:
        return None

    # "Book chapter:verse" or "Book chapter:verse-verse"
    m = re.match(r"^(.+?)\s+(\d+):(\d+)(?:-(\d+))?$", text, re.IGNORECASE)
    if m:
        book = m.group(1).strip()
        ch = int(m.group(2))
        v1 = int(m.group(3))
        v2 = int(m.group(4)) if m.group(4) else v1
        return (book, ch, v1, v2)

    # "Book: verse" or "Book: verse-verse" (chapter missing; caller may infer)
    m = re.match(r"^(.+?):\s*(\d+)(?:-(\d+))?$", text, re.IGNORECASE)
    if m:
        book = m.group(1).strip()
        v1 = int(m.group(2))
        v2 = int(m.group(3)) if m.group(3) else v1
        return (book, None, v1, v2)

    # "Book chapter" (no verse)
    m = re.match(r"^(.+?)\s+(\d+)$", text, re.IGNORECASE)
    if m:
        book = m.group(1).strip()
        ch = int(m.group(2))
        return (book, ch, None, None)

    return None


def _extract_refs_from_segment(
    segment: str,
    last_chapter_by_book: Optional[Dict[str, int]] = None,
) -> Tuple[List[Tuple[str, Optional[int], Optional[int], Optional[int]]], Dict[str, int]]:
    """
    Split segment by comma and parse each part. Handles "Mark 1:3-5, 7" (verse 7 = same book/chapter)
    and "John 3:5, Mark: 7" (Mark: 7 uses last seen chapter for Mark).
    Returns (refs, updated last_chapter_by_book).
    """
    parts = [p.strip() for p in segment.split(",") if p.strip()]
    refs: List[Tuple[str, Optional[int], Optional[int], Optional[int]]] = []
    last_book: Optional[str] = None
    last_chapter: Optional[int] = None
    by_book: Dict[str, int] = dict(last_chapter_by_book) if last_chapter_by_book else {}

    for part in parts:
        parsed = _parse_single_ref(part)
        if parsed:
            book, ch, v1, v2 = parsed
            if ch is not None:
                last_book, last_chapter = book, ch
                by_book[book] = ch
            elif v1 is not None:
                if book in by_book:
                    ch = by_book[book]
                elif last_book is not None and last_chapter is not None:
                    book, ch = last_book, last_chapter
                else:
                    ch = None
                refs.append((book, ch, v1, v2))
            else:
                refs.append((book, ch, v1, v2))
        else:
            only_verse = re.match(r"^(\d+)$", part)
            if only_verse and last_book is not None and last_chapter is not None:
                v = int(only_verse.group(1))
                refs.append((last_book, last_chapter, v, v))

    return refs, by_book


def _merge_verse_ranges(ranges: List[Tuple[int, int]]) -> List[Tuple[int, int]]:
    """Sort and merge overlapping or adjacent verse ranges."""
    if not ranges:
        return []
    sorted_r = sorted(set(ranges))
    merged = [sorted_r[0]]
    for a, b in sorted_r[1:]:
        pa, pb = merged[-1]
        if a <= pb + 1:
            merged[-1] = (pa, max(pb, b))
        else:
            merged.append((a, b))
    return merged


def format_reference(raw: str) -> str:
    """
    Normalize and format a Bible reference string.

    Example:
        "Mark 1:3-5; John 3:5, Mark: 7" -> "Mark 1:3–5, 7; 1 John 3:5"
    Groups by book, then chapter, then verse ranges. Uses en-dash (–) for ranges.
    """
    if not raw or not raw.strip():
        return raw

    raw = re.sub(r"\s+", " ", raw.strip())
    segments = [s.strip() for s in raw.split(";") if s.strip()]

    all_refs: List[Tuple[str, Optional[int], Optional[int], Optional[int]]] = []
    last_chapter_by_book: Dict[str, int] = {}
    for seg in segments:
        refs, last_chapter_by_book = _extract_refs_from_segment(seg, last_chapter_by_book)
        all_refs.extend(refs)

    # Group by (book, chapter)
    by_key: Dict[Tuple[str, Optional[int]], List[Tuple[Optional[int], Optional[int]]]] = defaultdict(list)
    for book, ch, v1, v2 in all_refs:
        key = (book, ch)
        if v1 is not None and v2 is not None:
            by_key[key].append((v1, v2))
        elif ch is not None:
            by_key[key].append((None, None))

    # Build output parts
    def sort_key(item):
        (book, ch), _ = item
        return (book, ch or 0)

    out_parts = []
    for (book, chapter), verse_ranges in sorted(by_key.items(), key=sort_key):
        verse_ranges = _merge_verse_ranges([(a, b) for a, b in verse_ranges if a is not None and b is not None])
        if not verse_ranges and chapter is not None:
            out_parts.append(f"{book} {chapter}")
        elif verse_ranges and chapter is not None:
            v_strs = [f"{a}{EN_DASH}{b}" if a != b else str(a) for a, b in verse_ranges]
            out_parts.append(f"{book} {chapter}:{', '.join(v_strs)}")
        elif verse_ranges:
            v_strs = [f"{a}{EN_DASH}{b}" if a != b else str(a) for a, b in verse_ranges]
            out_parts.append(f"{book} {', '.join(v_strs)}")

    return "; ".join(out_parts)
