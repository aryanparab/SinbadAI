"""Canonical campaign snapshots and deterministic state transitions."""
import json
import os
import sqlite3
from routes import encounters
from pathlib import Path
from contextlib import contextmanager
from datetime import datetime, timezone

DB_PATH = Path(os.getenv("CAMPAIGN_DB_PATH", "data/campaigns.sqlite3"))

@contextmanager
def connect():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    try:
        conn.execute("CREATE TABLE IF NOT EXISTS campaigns (id TEXT PRIMARY KEY, data TEXT NOT NULL)")
        with conn:
            yield conn
    finally:
        conn.close()

def load(session_id):
    with connect() as conn:
        row = conn.execute("SELECT data FROM campaigns WHERE id=?", (session_id,)).fetchone()
    return json.loads(row[0]) if row else None

def save(session_id, data):
    with connect() as conn:
        conn.execute("INSERT OR REPLACE INTO campaigns VALUES (?, ?)", (session_id, json.dumps(data)))

def apply_inventory(previous, changes):
    items = {i.name.casefold(): i.model_copy(deep=True) for i in previous}
    for item in changes.removed_items:
        key = item.name.casefold()
        if key not in items or item.quantity > items[key].quantity:
            raise ValueError(f"Cannot remove unavailable item: {item.name}")
        items[key].quantity -= item.quantity
    for item in changes.modified_items:
        key = item.name.casefold()
        if key not in items:
            raise ValueError(f"Cannot modify unavailable item: {item.name}")
        # Quantity changes belong in added/removed, never in modified.
        items[key] = item.model_copy(update={"quantity": items[key].quantity})
    for item in changes.added_items:
        key = item.name.casefold()
        if key in items:
            items[key].quantity += item.quantity
        else:
            items[key] = item.model_copy(deep=True)
    return [item for item in items.values() if item.quantity > 0]

def phase(turn, total):
    ratio = turn / total
    return "resolution" if turn == total else "climax" if ratio >= .8 else "rising action" if ratio > .2 else "setup"

def reconcile(input, scene, turn, total, plan):
    scene.current_inventory = apply_inventory(input.current_inventory, scene.inventory_changes)
    state, old = scene.game_state, input.game_state
    state.relationships = {**old.relationships, **state.relationships}
    for char_id, delta in scene.relationship_changes.items():
        state.relationships[char_id] = max(-10, min(10, old.relationships.get(char_id, 0) + delta))
    for char in scene.characters:
        if char.id not in state.relationships:
            state.relationships[char.id] = char.relationship_level
        char.relationship_level = state.relationships[char.id]
    state.story_flags = {**old.story_flags, **state.story_flags, "turn": turn, "total_turns": total, "is_complete": turn == total, "story_phase": phase(turn, total)}
    previous_cast = old.story_flags.get("cast", {})
    cast = {**previous_cast, **{c.id: c.model_dump() for c in scene.characters}}
    state.story_flags["cast"] = cast
    names = {key: character.get("name", key) for key, character in cast.items()}
    for line in scene.dialogue:
        line.speaker = names.get(line.speaker, line.speaker)
    state.story_flags["presentation"] = {
        "scene_title": scene.scene_title or scene.location,
        "chapter_title": scene.chapter_title or "The adventure continues",
        "mission": scene.mission.model_dump() if scene.mission else old.story_flags.get("presentation", {}).get("mission"),
        "choice_stakes": scene.choice_stakes,
        "ending_summary": scene.ending_summary,
    }
    state.story_flags["encounter_history"] = old.story_flags.get("encounter_history", [])
    state.story_flags["encounter"] = None
    if scene.encounter and turn < total:
        state.story_flags["encounter"] = encounters.create(scene.encounter, turn)
    if turn == total:
        state.story_flags["encounter"] = None
    state.location_flags = {**old.location_flags, **state.location_flags}
    state.reputation = {**old.reputation, **state.reputation}
    state.revealed_secrets = list(dict.fromkeys(old.revealed_secrets + state.revealed_secrets + scene.new_secrets))
    state.major_events = list(dict.fromkeys(old.major_events + state.major_events))
    state.completed_objectives = list(dict.fromkeys(old.completed_objectives + state.completed_objectives + scene.completed_objectives_this_scene))
    state.failed_objectives = list(dict.fromkeys(old.failed_objectives + state.failed_objectives))
    objectives = {o.id: o for o in old.active_objectives + state.active_objectives + scene.new_objectives}
    for obj in objectives.values():
        if obj.completed and obj.id not in state.completed_objectives:
            state.completed_objectives.append(obj.id)
    resolved = set(state.completed_objectives + state.failed_objectives)
    state.active_objectives = [o for o in objectives.values() if o.id not in resolved]
    if turn == total:
        state.failed_objectives = list(dict.fromkeys(state.failed_objectives + [o.id for o in state.active_objectives]))
        state.active_objectives = []
        scene.options = []
        scene.interactive_elements = []
        scene.threat_updates = []
    return scene


def reserve_generation():
    """Atomically cap model invocations across all guests, including failures."""
    limit = max(0, int(os.getenv("DAILY_AI_CALL_LIMIT", "100")))
    day = datetime.now(timezone.utc).date().isoformat()
    with connect() as conn:
        conn.execute("CREATE TABLE IF NOT EXISTS generation_usage (day TEXT PRIMARY KEY, calls INTEGER NOT NULL)")
        conn.execute("INSERT OR IGNORE INTO generation_usage VALUES (?, 0)", (day,))
        updated = conn.execute("UPDATE generation_usage SET calls=calls+1 WHERE day=? AND calls < ?", (day, limit))
        return updated.rowcount == 1
