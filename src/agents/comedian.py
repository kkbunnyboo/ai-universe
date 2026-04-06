"""
Comedian agent – an AI agent that fetches and tells jokes.
"""

from typing import Dict, List, Optional

from src.services.joke_service import fetch_joke, fetch_jokes_batch


class ComedianAgent:
    """
    An AI agent specialised in joke-telling.

    It uses the joke_service to fetch jokes from JokeAPI.dev and formats
    them into conversational responses.
    """

    name: str = "Comedian"
    description: str = "An AI comedian that can fetch and tell jokes of various categories."
    personality: str = (
        "Friendly, witty, and light-hearted. Always looking to make you smile. "
        "Uses timing and delivery to enhance punchlines."
    )

    SUPPORTED_CATEGORIES: List[str] = ["any", "general", "programming", "knock-knock", "dark", "pun"]

    async def tell_joke(self, category: str = "any", safe: bool = True) -> str:
        """
        Fetch a joke and format it as a conversational message.

        Args:
            category: Joke category to fetch from.
            safe: Whether to restrict to safe / family-friendly jokes.

        Returns:
            A formatted string ready to send to the user.
        """
        joke = await fetch_joke(category=category, safe_mode=safe)
        return self._format_joke_message(joke)

    async def tell_jokes(
        self,
        category: str = "any",
        count: int = 3,
        safe: bool = True,
    ) -> List[str]:
        """
        Fetch multiple jokes and format them.

        Args:
            category: Joke category.
            count: Number of jokes (1-10).
            safe: Whether to restrict to safe content.

        Returns:
            List of formatted joke strings.
        """
        jokes = await fetch_jokes_batch(category=category, count=count, safe_mode=safe)
        return [self._format_joke_message(j) for j in jokes]

    def _format_joke_message(self, joke: Dict) -> str:
        """Convert a normalised joke dict into a human-readable message."""
        category_emoji = {
            "programming": "💻",
            "pun": "🥁",
            "dark": "🖤",
            "misc": "😄",
            "spooky": "👻",
        }.get(joke["category"].lower(), "😂")

        header = f"{category_emoji} *{joke['category'].title()} Joke*\n\n"

        if joke["is_two_part"]:
            return f"{header}❓ {joke['setup']}\n\n💬 {joke['delivery']}"
        return f"{header}{joke['joke']}"

    def introduce(self) -> str:
        """Return a friendly introduction from the comedian."""
        return (
            "🎤 Hey there! I'm your AI Comedian! "
            "I can tell you jokes about programming, puns, knock-knock style, and more. "
            "Just ask me to tell you a joke and I'll have you laughing in no time! 😄"
        )
