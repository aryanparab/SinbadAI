# memory_service.py
from agno.memory.v2.schema import UserMemory
from agno.memory.v2.db.schema import MemoryRow
from typing import List, Optional, Dict, Any
import logging
import json
from datetime import datetime, timezone

logger = logging.getLogger(__name__)


def _build_narrative_summary(game_data: Dict[str, Any]) -> str:
    """
    Build a concise natural-language summary from game_data.

    This is what Agno injects as text into the agent's context window on
    subsequent turns — so it must be readable prose, NOT raw JSON.
    Keeping it tight (< ~400 tokens) avoids bloating the context across
    many saved scenes.
    """
    parts = []

    # Scene location & tag
    scene_tag = game_data.get("scene_tag", "unknown_scene")
    location  = game_data.get("location", "unknown location")
    world     = game_data.get("world", "")
    scenes_completed = game_data.get("scenes_completed", 0)
    parts.append(
        f"[Scene {scenes_completed}: {scene_tag}] Location: {location}"
        + (f" ({world})" if world else "") + "."
    )

    # What happened this scene
    history_entry = game_data.get("history_entry", "")
    if history_entry:
        parts.append(f"What happened: {history_entry}")

    # Recent history (last 5 entries)
    recent = game_data.get("history", [])
    if recent:
        last_5 = recent[-5:]
        parts.append("Recent history: " + " | ".join(last_5) + ".")

    gs = game_data.get("game_state", {})

    # Active objectives
    active_objs = gs.get("active_objectives", [])
    if active_objs:
        descs = []
        for o in active_objs[:4]:
            if isinstance(o, dict):
                descs.append(o.get("description", str(o)))
            else:
                descs.append(str(o))
        parts.append("Active objectives: " + "; ".join(descs) + ".")

    # Major events (last 3)
    major_events = gs.get("major_events", [])
    if major_events:
        parts.append("Major story events: " + "; ".join(str(e) for e in major_events[-3:]) + ".")

    # Relationships (top 5)
    relationships = gs.get("relationships", {})
    if relationships:
        rel_str = ", ".join(
            f"{k}: {v}/10" for k, v in list(relationships.items())[:5]
        )
        parts.append(f"Relationships: {rel_str}.")

    # Reputation
    reputation = gs.get("reputation", {})
    if reputation:
        rep_str = ", ".join(f"{k}: {v}" for k, v in list(reputation.items())[:4])
        parts.append(f"Faction reputation: {rep_str}.")

    # Inventory (names only, top 6)
    inventory = game_data.get("inventory", [])
    if inventory:
        item_names = []
        for i in inventory[:6]:
            item_names.append(i.get("name", str(i)) if isinstance(i, dict) else str(i))
        parts.append("Inventory: " + ", ".join(item_names) + ".")

    # Revealed secrets (last 2)
    secrets = gs.get("revealed_secrets", [])
    if secrets:
        parts.append("Known secrets: " + "; ".join(str(s) for s in secrets[-2:]) + ".")

    return " ".join(parts)


def add_game_memory(memory_instance, session_id: str, game_data: Dict[str, Any]) -> bool:
    """
    Store game memory using Agno's MemoryRow (what upsert_memory actually expects).

    MemoryRow.memory is Dict[str, Any] — we store both the narrative summary
    (for Agno context injection) and the full game_data (for load/save) inside it.
    The SQLite backend serialises memory via str() and deserialises via eval().
    """
    try:
        narrative_summary = _build_narrative_summary(game_data)

        # MemoryRow.memory must be a dict — pack both the prose summary and
        # the full structured data so nothing is lost.
        memory_payload: Dict[str, Any] = {
            # Agno injects this field as the agent's context text on next turn.
            "memory": narrative_summary,
            # Full structured data — used by the /load endpoint.
            "game_data": game_data,
            # Index fields for quick querying / display.
            "scene_tag": game_data.get("scene_tag"),
            "location": game_data.get("location"),
            "world": game_data.get("world"),
            "scenes_completed": game_data.get("scenes_completed", 0),
        }

        if hasattr(memory_instance, 'db'):
            memory_row = MemoryRow(
                user_id=session_id,
                memory=memory_payload,
                last_updated=datetime.now(timezone.utc),
            )
            memory_instance.db.upsert_memory(memory_row)
            logger.info(f"Added game memory for session {session_id} (MemoryRow, narrative summary)")
        else:
            # Fallback: Agno public API only stores the narrative string.
            memory_instance.add_user_memory(
                user_id=session_id,
                memory=UserMemory(memory=narrative_summary)
            )
            logger.info(f"Added game memory for session {session_id} (Agno wrapper, narrative summary)")

        return True

    except Exception as e:
        logger.error(f"Error adding game memory for session {session_id}: {e}", exc_info=True)
        return False

def get_user_memories(memory_instance, session_id: str) -> List[UserMemory]:
    """
    Get memories with proper parsing.

    read_memories() returns MemoryRow objects (Pydantic models).
    MemoryRow.memory is a dict that we stored via add_game_memory — it contains
    both "memory" (narrative string) and "game_data" (full structured data).
    """
    try:
        if hasattr(memory_instance, 'db'):
            # read_memories returns List[MemoryRow] — each .memory is a dict
            memory_rows: List[MemoryRow] = memory_instance.db.read_memories(
                user_id=session_id
            )

            user_memories = []
            for row in memory_rows:
                # row.memory is the dict we stored; fall back gracefully if format changed
                mem_dict: Dict[str, Any] = row.memory if isinstance(row.memory, dict) else {}

                # Prefer game_data for structured load/save; fall back to raw memory string
                if "game_data" in mem_dict:
                    memory_content = json.dumps(mem_dict["game_data"], default=str)
                elif "memory" in mem_dict:
                    memory_content = mem_dict["memory"]
                else:
                    memory_content = json.dumps(mem_dict, default=str)

                user_memories.append(UserMemory(
                    memory_id=row.id,
                    memory=memory_content,
                    last_updated=row.last_updated,
                ))

            logger.info(f"Retrieved {len(user_memories)} memories for session {session_id}")
            return user_memories
        else:
            memories = memory_instance.get_user_memories(user_id=session_id)
            logger.info(f"Retrieved {len(memories)} memories for session {session_id}")
            return memories

    except Exception as e:
        logger.error(f"Error retrieving memories for session {session_id}: {e}", exc_info=True)
        return []
    

def clear_user_memories(memory_instance, session_id: str) -> bool:
    """
    Clear all memories for a session.

    db.clear() takes NO arguments — it wipes the whole table.
    For per-session deletion we must delete rows one by one using delete_memory().
    """
    try:
        if hasattr(memory_instance, 'db'):
            # read_memories filters by user_id; then delete each row individually
            memory_rows: List[MemoryRow] = memory_instance.db.read_memories(
                user_id=session_id
            )
            for row in memory_rows:
                if row.id:
                    memory_instance.db.delete_memory(row.id)
            logger.info(
                f"Cleared {len(memory_rows)} memories for session {session_id} (direct DB)"
            )
        else:
            memories = get_user_memories(memory_instance, session_id)
            for memory_item in memories:
                if memory_item.memory_id:
                    memory_instance.delete_user_memory(
                        user_id=session_id,
                        memory_id=memory_item.memory_id
                    )
            logger.info(f"Cleared all memories for session {session_id} (Agno wrapper)")

        return True

    except Exception as e:
        logger.error(f"Error clearing memories for session {session_id}: {e}", exc_info=True)
        return False

def search_memories(memory_instance, session_id: str, query: str, limit: int = 10) -> List[UserMemory]:
    """
    Search memories by query string
    """
    try:
        results = memory_instance.search_user_memories(
            query=query,
            limit=limit,
            user_id=session_id
        )
        
        logger.info(f"Found {len(results)} memories for query '{query}' in session {session_id}")
        return results
        
    except Exception as e:
        logger.error(f"Error searching memories for session {session_id}: {e}")
        return []

def get_latest_memories(memory_instance, session_id: str, limit: int = 5) -> List[UserMemory]:
    """
    Get the most recent N memories for a session
    """
    try:
        memories = get_user_memories(memory_instance, session_id)
        
        # Sort by last_updated if available, otherwise return last N
        if memories:
            sorted_memories = sorted(
                memories, 
                key=lambda x: x.last_updated if x.last_updated else x.memory_id or "",
                reverse=True
            )
            return sorted_memories[:limit]
        
        return []
        
    except Exception as e:
        logger.error(f"Error getting latest memories for session {session_id}: {e}")
        return []

def extract_scene_state_from_memory(memory_summary: str) -> Dict[str, Any]:
    """
    Extract scene state from memory string
    """
    try:
        state = memory_summary["world"][:100]
        return state
        
    except Exception as e:
        logger.error(f"Error extracting scene state from memory: {e}")
        return {
            "location": "unknown",
            "inventory": [],
            "health": 100,
            "sanity": 100,
            "last_narration": memory_summary[-300:] if memory_summary else ""
        }

def has_user_memories(memory_instance, session_id: str) -> bool:
    """
    Check if a user has any stored memories
    
    Args:
        memory_instance: The memory database instance
        session_id: User/session identifier
        
    Returns:
        bool: True if user has memories, False otherwise
    """
    try:
        memories = get_user_memories(memory_instance, session_id)
        return len(memories) > 0
        
    except Exception as e:
        logger.error(f"Error checking memories for session {session_id}: {e}")
        return False

def get_memory_summary(memory_instance, session_id: str) -> str:
    """
    Get a combined summary of all memories for a user
    
    Args:
        memory_instance: The memory database instance
        session_id: User/session identifier
        
    Returns:
        Combined memory summary string
    """
    try:
        memories = get_user_memories(memory_instance, session_id)
        
        if not memories:
            return "No memories found."
        
        # Combine all memory contents
        combined_memory = "\n\n".join([m.memory for m in memories])
        return combined_memory
        
    except Exception as e:
        logger.error(f"Error getting memory summary for session {session_id}: {e}")
        return "Error retrieving memories."

def get_latest_game_state(memory_instance, session_id: str) -> Optional[Dict[str, Any]]:
    """
    Get the most recent complete game state for resuming
    
    Args:
        memory_instance: The memory database instance
        session_id: User/session identifier
        
    Returns:
        Dict with complete game state or None
    """
    try:
        if hasattr(memory_instance, 'db'):
            # Get latest from database directly
            latest = memory_instance.db.get_latest(session_id)
            
            if latest and "game_data" in latest:
                logger.info(f"Retrieved latest game state for session {session_id}")
                return latest["game_data"]
            elif latest and "memory" in latest:
                # Parse from JSON string
                return json.loads(latest["memory"])
        else:
            # Fallback to Agno method
            memories = get_latest_memories(memory_instance, session_id, limit=1)
            if memories:
                return json.loads(memories[0].memory)
        
        logger.warning(f"No game state found for session {session_id}")
        return None
        
    except Exception as e:
        logger.error(f"Error getting latest game state for session {session_id}: {e}")
        return None