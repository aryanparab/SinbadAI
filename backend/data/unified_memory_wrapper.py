"""
Unified Database Wrapper for Agno Memory
Works with both SQLite and MongoDB seamlessly
"""

import logging
from typing import Optional, Dict, Any, List

logger = logging.getLogger(__name__)

class UnifiedMemoryDb:
    """
    Wrapper that provides a unified interface for both SQLite and MongoDB
    Handles method name differences between the two databases
    """
    
    def __init__(self, db_instance):
        """
        Initialize with either SqliteMemoryDb or MongoMemoryDb instance
        
        Args:
            db_instance: Instance of SqliteMemoryDb or MongoMemoryDb
        """
        self._db = db_instance
        self._db_type = type(db_instance).__name__
        logger.info(f"🔗 Unified wrapper initialized for: {self._db_type}")
    
    def insert(self, row: Dict[str, Any]) -> Dict[str, Any]:
        """Insert a row - works with both SQLite and MongoDB"""
        if hasattr(self._db, 'insert'):
            # MongoDB has insert method
            return self._db.insert(row)
        else:
            # SQLite uses upsert
            return self._db.upsert(row)
    
    def upsert(self, row: Dict[str, Any]) -> Dict[str, Any]:
        """Upsert a row - works with both SQLite and MongoDB"""
        return self._db.upsert(row)
    
    def select_all(self, user_id: Optional[str] = None, limit: int = 100) -> List[Dict[str, Any]]:
        """Select all rows - works with both SQLite and MongoDB"""
        if hasattr(self._db, 'select_all'):
            return self._db.select_all(user_id=user_id, limit=limit)
        else:
            # Fallback for SQLite if needed
            return self._db.read_memories(user_id=user_id) if hasattr(self._db, 'read_memories') else []
    
    def delete(self, id: str) -> bool:
        """Delete by id - works with both SQLite and MongoDB"""
        if hasattr(self._db, 'delete'):
            return self._db.delete(id)
        else:
            # SQLite might use different method
            try:
                self._db.delete_memory(id)
                return True
            except:
                return False
    
    def clear(self, user_id: Optional[str] = None):
        """Clear memories - works with both SQLite and MongoDB"""
        if hasattr(self._db, 'clear'):
            self._db.clear(user_id)
        else:
            # SQLite alternative
            try:
                if user_id:
                    self._db.clear_user_memories(user_id)
                else:
                    self._db.clear_all()
            except Exception as e:
                logger.warning(f"Could not clear memories: {e}")
    
    def get_latest(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get latest memory - works with both SQLite and MongoDB"""
        if hasattr(self._db, 'get_latest'):
            return self._db.get_latest(user_id)
        else:
            # Fallback
            memories = self.select_all(user_id=user_id, limit=1)
            return memories[0] if memories else None
    
    def search(self, user_id: str, query: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Search memories - works with both SQLite and MongoDB"""
        if hasattr(self._db, 'search'):
            return self._db.search(user_id, query)
        else:
            # Basic fallback
            return self.select_all(user_id=user_id)
    
    def __getattr__(self, name):
        """
        Proxy any other method calls to the underlying database
        This allows direct access to database-specific methods if needed
        """
        return getattr(self._db, name)
    
    @property
    def db_type(self) -> str:
        """Return the underlying database type"""
        return self._db_type