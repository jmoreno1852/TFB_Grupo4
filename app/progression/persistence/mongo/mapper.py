from datetime import datetime, timezone
from typing import Any, Dict

from progression.domain.entities import Progression, Stats


def doc_to_progression(doc: Dict[str, Any]) -> Progression:
    """
    Mongo doc to Progression domain entity.
    Applies defaults if fields are missing.
    """
    stats_doc = doc.get("stats") or {}

    return Progression(
        user_id=doc["user_id"],
        level=int(doc.get("level", 1)),
        xp=int(doc.get("xp", 0)),
        gold=int(doc.get("gold", 0)),
        stats=Stats(
            strength=int(stats_doc.get("strength", 0)),
            focus=int(stats_doc.get("focus", 0)),
            resilience=int(stats_doc.get("resilience", 0)),
        ),
        created_at=doc.get("created_at") or datetime.now(timezone.utc),
        updated_at=doc.get("updated_at"),
    )


def progression_to_doc(progression: Progression) -> Dict[str, Any]:
    """
    Progression domain entity to Mongo document.
    """
    doc: Dict[str, Any] = {
        "user_id": progression.user_id,
        "level": progression.level,
        "xp": progression.xp,
        "gold": progression.gold,
        "stats": {
            "strength": progression.stats.strength,
            "focus": progression.stats.focus,
            "resilience": progression.stats.resilience,
        },
        "created_at": progression.created_at,
        "updated_at": progression.updated_at,
    }

    return doc
