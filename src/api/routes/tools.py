"""
Joke tool endpoints – /api/v1/tools/jokes
"""

import logging
from typing import List, Optional

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from fastapi import Depends

from src.database.db import get_db
from src.models.database import FavoriteJoke
from src.services.joke_service import fetch_joke, fetch_jokes_batch

logger = logging.getLogger(__name__)
router = APIRouter()

VALID_CATEGORIES = {"any", "general", "programming", "knock-knock", "dark", "pun"}


class JokeResponse(BaseModel):
    id: str
    category: str
    is_two_part: bool
    setup: Optional[str] = None
    delivery: Optional[str] = None
    joke: Optional[str] = None
    flags: dict = Field(default_factory=dict)
    safe: bool = True
    language: str = "en"


class FavoriteJokeRequest(BaseModel):
    joke_id: str
    category: str
    setup: Optional[str] = None
    delivery: Optional[str] = None
    joke_text: Optional[str] = None
    is_two_part: bool = False


class FavoriteJokeResponse(BaseModel):
    id: int
    joke_id: str
    category: str
    setup: Optional[str] = None
    delivery: Optional[str] = None
    joke_text: Optional[str] = None
    is_two_part: bool

    class Config:
        from_attributes = True


@router.get("/jokes", response_model=JokeResponse, summary="Get a random joke")
async def get_joke(
    category: str = Query("any", description="Joke category: any, general, programming, knock-knock, dark, pun"),
    safe: bool = Query(True, description="Return only safe/family-friendly jokes"),
):
    """
    Fetch a random joke from JokeAPI.dev.

    Supported categories: `any`, `general`, `programming`, `knock-knock`, `dark`, `pun`.
    Results are cached for 5 minutes to avoid hammering the external API.
    """
    if category not in VALID_CATEGORIES:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid category '{category}'. Choose from: {', '.join(sorted(VALID_CATEGORIES))}",
        )
    try:
        joke = await fetch_joke(category=category, safe_mode=safe)
        return joke
    except RuntimeError as exc:
        logger.error("Joke fetch failed: %s", exc)
        raise HTTPException(status_code=502, detail=str(exc))


@router.get("/jokes/batch", response_model=List[JokeResponse], summary="Get multiple jokes")
async def get_jokes_batch(
    category: str = Query("any", description="Joke category"),
    count: int = Query(5, ge=1, le=10, description="Number of jokes (1-10)"),
    safe: bool = Query(True, description="Return only safe jokes"),
):
    """Fetch a batch of jokes (up to 10) from JokeAPI.dev."""
    if category not in VALID_CATEGORIES:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid category '{category}'. Choose from: {', '.join(sorted(VALID_CATEGORIES))}",
        )
    try:
        jokes = await fetch_jokes_batch(category=category, count=count, safe_mode=safe)
        return jokes
    except RuntimeError as exc:
        logger.error("Joke batch fetch failed: %s", exc)
        raise HTTPException(status_code=502, detail=str(exc))


@router.get("/jokes/categories", summary="List available joke categories")
async def get_categories():
    """Return the list of supported joke categories."""
    return {
        "categories": sorted(VALID_CATEGORIES),
        "descriptions": {
            "any": "Random joke from any category",
            "general": "General / miscellaneous jokes",
            "programming": "Programming and tech jokes",
            "knock-knock": "Knock-knock jokes",
            "dark": "Dark humour jokes",
            "pun": "Puns and wordplay",
        },
    }


@router.post("/jokes/favorites", response_model=FavoriteJokeResponse, status_code=201, summary="Save a favorite joke")
async def save_favorite(
    body: FavoriteJokeRequest,
    db: Session = Depends(get_db),
):
    """Bookmark a joke as a favourite."""
    existing = db.query(FavoriteJoke).filter(FavoriteJoke.joke_id == body.joke_id).first()
    if existing:
        return existing

    fav = FavoriteJoke(
        joke_id=body.joke_id,
        category=body.category,
        setup=body.setup,
        delivery=body.delivery,
        joke_text=body.joke_text,
        is_two_part=body.is_two_part,
    )
    db.add(fav)
    db.commit()
    db.refresh(fav)
    return fav


@router.get("/jokes/favorites", response_model=List[FavoriteJokeResponse], summary="List favorite jokes")
async def list_favorites(db: Session = Depends(get_db)):
    """Return all bookmarked jokes."""
    return db.query(FavoriteJoke).order_by(FavoriteJoke.saved_at.desc()).all()


@router.delete("/jokes/favorites/{joke_id}", status_code=204, summary="Remove a favorite joke")
async def remove_favorite(joke_id: str, db: Session = Depends(get_db)):
    """Remove a joke from favourites."""
    fav = db.query(FavoriteJoke).filter(FavoriteJoke.joke_id == joke_id).first()
    if not fav:
        raise HTTPException(status_code=404, detail="Favourite joke not found")
    db.delete(fav)
    db.commit()
