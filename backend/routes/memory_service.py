# memory_service.py
from agno.memory.v2.schema import UserMemory
from typing import List, Optional, Dict, Any
import logging
import json

logger = logging.getLogger(__name__)

def add_game_memory(memory_instance, session_id: str, game_data: Dict[str, Any]) -> bool:

    try:
        memory_summary = game_data
 
        
        memory_instance.add_user_memory(
            user_id=session_id,
            memory=UserMemory(memory=json.dumps(memory_summary))
        )
  
        logger.info(f"Added game memory for session {session_id}")
        return True
        
    except Exception as e:
        logger.error(f"Error adding game memory for session {session_id}: {e}")
        return False

def get_user_memories(memory_instance, session_id: str) -> List[UserMemory]:

    try:
        
        memories = memory_instance.get_user_memories(user_id=session_id)
        
        logger.info(f"Retrieved {len(memories)} memories for session {session_id}")
        return memories
        
    except Exception as e:
        logger.error(f"Error retrieving memories for session {session_id}: {e}")
        return []

def clear_user_memories(memory_instance, session_id: str) -> bool:
   
    try:
        # Get all memories first
        memories = get_user_memories(memory_instance, session_id)
        
        # Delete each memory
        for memory_item in memories:
            if memory_item.memory_id:
                memory_instance.delete_user_memory(
                    user_id=session_id,
                    memory_id=memory_item.memory_id
                )
        
        logger.info(f"Cleared all memories for session {session_id}")
        return True
        
    except Exception as e:
        logger.error(f"Error clearing memories for session {session_id}: {e}")
        return False

def search_memories(memory_instance, session_id: str, query: str, limit: int = 10) -> List[UserMemory]:

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
    

