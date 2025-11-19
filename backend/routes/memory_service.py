# memory_service.py
from agno.memory.v2.schema import UserMemory
from typing import List, Optional, Dict, Any
import logging
import json
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

def add_game_memory(memory_instance, session_id: str, game_data: Dict[str, Any]) -> bool:
    """
    Store game memory with proper structure for MongoDB
    """
    try:
        # ⭐ Store directly to the database for better structure
        memory_dict = {
            "user_id": session_id,
            "session_id": session_id,
            "created_at": datetime.now(timezone.utc),  # ⭐ Fixed deprecated utcnow()
            "last_updated": datetime.now(timezone.utc),
            
            # Store the actual game data at top level for easy access
            "game_data": game_data,
            
            # Also store as JSON string for Agno compatibility
            "memory": json.dumps(game_data),
            
            # Extract key fields for easy querying
            "scene_tag": game_data.get("scene_tag"),
            "location": game_data.get("location"),
            "world": game_data.get("world"),
            "scenes_completed": game_data.get("scenes_completed", 0),
        }
        
        # Use the database directly for better control
        if hasattr(memory_instance, 'db'):
            # Access the underlying database
            result = memory_instance.db.upsert_memory(memory_dict)
            logger.info(f"Added game memory for session {session_id} (direct DB)")
        else:
            # Fallback to Agno's method
            memory_instance.add_user_memory(
                user_id=session_id,
                memory=UserMemory(memory=json.dumps(game_data))
            )
            logger.info(f"Added game memory for session {session_id} (Agno wrapper)")
        
        return True
        
    except Exception as e:
        logger.error(f"Error adding game memory for session {session_id}: {e}")
        import traceback
        traceback.print_exc()
        return False

def get_user_memories(memory_instance, session_id: str) -> List[UserMemory]:
    """
    Get memories with proper parsing
    """
    try:
        # Try to get from database directly first for better structure
        if hasattr(memory_instance, 'db'):
            memories = memory_instance.db.read_memories(session_id)
            
            # Convert to UserMemory objects
            user_memories = []
            for mem in memories:
                # If we have game_data field, use it
                if "game_data" in mem:
                    memory_content = json.dumps(mem["game_data"])
                else:
                    # Fall back to memory field
                    memory_content = mem.get("memory", "{}")
                
                # ⭐ FIX: UserMemory doesn't take user_id parameter
                user_memories.append(UserMemory(
                    memory_id=mem.get("id"),
                    memory=memory_content
                    # ❌ Removed: user_id=session_id
                ))
            
            logger.info(f"Retrieved {len(user_memories)} memories for session {session_id}")
            return user_memories
        else:
            # Fallback to Agno's method
            memories = memory_instance.get_user_memories(user_id=session_id)
            logger.info(f"Retrieved {len(memories)} memories for session {session_id}")
            return memories
        
    except Exception as e:
        logger.error(f"Error retrieving memories for session {session_id}: {e}")
        import traceback
        traceback.print_exc()
        return []
    

def clear_user_memories(memory_instance, session_id: str) -> bool:
    """
    Clear all memories for a session
    """
    try:
        # Use database directly if available
        if hasattr(memory_instance, 'db'):
            memory_instance.db.clear(user_id=session_id)
            logger.info(f"Cleared all memories for session {session_id} (direct DB)")
        else:
            # Fallback to Agno's method
            memories = get_user_memories(memory_instance, session_id)
            
            # Delete each memory
            for memory_item in memories:
                if memory_item.memory_id:
                    memory_instance.delete_user_memory(
                        user_id=session_id,
                        memory_id=memory_item.memory_id
                    )
            
            logger.info(f"Cleared all memories for session {session_id} (Agno wrapper)")
        
        return True
        
    except Exception as e:
        logger.error(f"Error clearing memories for session {session_id}: {e}")
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