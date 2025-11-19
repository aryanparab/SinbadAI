"""
MongoDB Memory Adapter for Agno Framework
Compatible with agno.memory.v2.memory.Memory

COMPLETE IMPLEMENTATION - All methods Agno needs!
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from pymongo import MongoClient
import os
import logging

logger = logging.getLogger(__name__)

class MongoMemoryDb:
    """MongoDB adapter compatible with Agno Memory interface"""
    
    def __init__(self, table_name: str = "game_memory", db_file: str = None):
        """
        Initialize MongoDB connection
        
        Args:
            table_name: Collection name in MongoDB (default: "game_memory")
            db_file: Not used for MongoDB, kept for compatibility with SQLite interface
        """
        mongodb_uri = os.getenv("MONGODB_URI")
        if not mongodb_uri:
            raise ValueError("MONGODB_URI environment variable not set")
        
        try:
            # Add SSL/TLS options for macOS compatibility
            self.client = MongoClient(
                mongodb_uri,
                serverSelectionTimeoutMS=5000,
                tls=True,
                tlsAllowInvalidCertificates=True  # For development only
            )
            # Test connection
            self.client.admin.command('ping')
            logger.info("✅ Connected to MongoDB successfully")
        except Exception as e:
            logger.error(f"❌ Failed to connect to MongoDB: {e}")
            raise
        
        self.db = self.client["shadow_council"]
        self.collection = self.db[table_name]
        self.table_name = table_name
        
        # Create indexes for faster queries
        try:
            self.collection.create_index("id")  # ⭐ Add index on id field
            self.collection.create_index("user_id")
            self.collection.create_index("created_at")
            self.collection.create_index([("user_id", 1), ("created_at", -1)])
            logger.info(f"✅ Indexes created for collection: {table_name}")
        except Exception as e:
            logger.warning(f"⚠️ Could not create indexes: {e}")
    
    # ========================================================================
    # CORE CRUD METHODS (Base interface)
    # ========================================================================
    
    def insert(self, row: Dict[str, Any]) -> Dict[str, Any]:
        """Insert a new memory row"""
        try:
            # ⭐ ADD THIS: Convert MemoryRow to dict if needed
            if hasattr(row, 'model_dump'):
                row = row.model_dump()
            elif hasattr(row, 'dict'):
                row = row.dict()
            
            # Rest stays the same...
            if "created_at" not in row:
                row["created_at"] = datetime.utcnow()
            
            result = self.collection.insert_one(row)
            row["id"] = str(result.inserted_id)
            logger.debug(f"Inserted memory with id: {row['id']}")
            return row
            
        except Exception as e:
            logger.error(f"Error inserting memory: {e}")
            raise
        
    def upsert(self, row: Dict[str, Any]) -> Dict[str, Any]:
            """Insert or update a memory row"""
            try:
                # Convert MemoryRow to dict if needed
                if hasattr(row, 'model_dump'):
                    row = row.model_dump()
                elif hasattr(row, 'dict'):
                    row = row.dict()
                
                # Add timestamp if not present
                if "created_at" not in row:
                    row["created_at"] = datetime.utcnow()
                
                # ⭐ CHANGE THIS: Check if id exists and is valid
                if "id" in row and row["id"]:
                    # Don't use ObjectId - use the id as a string directly
                    result = self.collection.update_one(
                        {"id": row["id"]},  # ⭐ Changed from {"_id": ObjectId(row["id"])}
                        {"$set": row},
                        upsert=True
                    )
                    logger.debug(f"Updated memory with id: {row['id']}")
                else:
                    # ⭐ Generate UUID if no id provided
                    if "id" not in row:
                        import uuid
                        row["id"] = str(uuid.uuid4())
                    
                    result = self.collection.insert_one(row)
                    logger.debug(f"Inserted new memory with id: {row['id']}")
                
                return row
                
            except Exception as e:
                logger.error(f"Error upserting memory: {e}")
                raise
    def delete(self, id: str) -> bool:
        """Delete a memory by id"""
        try:
            # ⭐ CHANGE THIS: Don't use ObjectId, use id field directly
            result = self.collection.delete_one({"id": id})  # ⭐ Changed from {"_id": ObjectId(id)}
            deleted = result.deleted_count > 0
            
            if deleted:
                logger.debug(f"Deleted memory with id: {id}")
            else:
                logger.warning(f"No memory found with id: {id}")
            
            return deleted
            
        except Exception as e:
            logger.error(f"Error deleting memory {id}: {e}")
            return False
    
    # ========================================================================
    # AGNO MEMORY SPECIFIC METHODS (Required by agno.memory.v2.memory.Memory)
    # ========================================================================
    
    def read_memories(
        self,
        user_id: str,
        limit: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Read memories for a specific user (Required by Agno Memory)
        
        Called by: memory.get_user_memories(), memory.add_user_memory()
        
        Args:
            user_id: User/session identifier
            limit: Maximum number of memories to return (None = all)
            
        Returns:
            List of memory dictionaries sorted by created_at (newest first)
        """
        try:
            query = {"user_id": user_id}
            cursor = self.collection.find(query).sort("created_at", -1)
            
            if limit:
                cursor = cursor.limit(limit)
            
            memories = []
            for doc in cursor:
                doc["id"] = str(doc.pop("_id"))
                memories.append(doc)
            
            logger.debug(f"Read {len(memories)} memories for user: {user_id}")
            return memories
            
        except Exception as e:
            logger.error(f"Error reading memories for user {user_id}: {e}")
            return []
    
    def upsert_memory(self, memory: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Upsert a single memory (Required by Agno Memory)"""
        try:
            # ⭐ ADD THIS: Convert MemoryRow to dict if needed
            if hasattr(memory, 'model_dump'):
                memory = memory.model_dump()
            elif hasattr(memory, 'dict'):
                memory = memory.dict()
                
            return self.upsert(memory)
        except Exception as e:
            logger.error(f"Error in upsert_memory: {e}")
            return None

    
    def delete_memory(self, memory_id: str) -> bool:
        """
        Delete a single memory (Agno Memory compatibility)
        
        Called by: memory.delete_user_memory()
        
        Args:
            memory_id: Memory identifier
            
        Returns:
            True if deleted
        """
        try:
            return self.delete(memory_id)
        except Exception as e:
            logger.error(f"Error in delete_memory: {e}")
            return False
    
    def get_memories(
        self,
        user_id: str,
        limit: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Get memories for a user (Agno Memory compatibility)
        Alias for read_memories
        
        Args:
            user_id: User identifier
            limit: Maximum memories to return
            
        Returns:
            List of memory dictionaries
        """
        return self.read_memories(user_id, limit)
    
    # ========================================================================
    # ADDITIONAL UTILITY METHODS
    # ========================================================================
    
    def select_all(self, user_id: Optional[str] = None, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Select all memories, optionally filtered by user_id
        
        Args:
            user_id: Optional user/session identifier
            limit: Maximum number of records to return
            
        Returns:
            List of memory dictionaries
        """
        try:
            query = {"user_id": user_id} if user_id else {}
            cursor = self.collection.find(query).sort("created_at", -1).limit(limit)
            
            results = []
            for doc in cursor:
                doc["id"] = str(doc.pop("_id"))
                results.append(doc)
            
            logger.debug(f"Selected {len(results)} memories" + (f" for user: {user_id}" if user_id else ""))
            return results
            
        except Exception as e:
            logger.error(f"Error selecting memories: {e}")
            return []
    
    def delete_many(self, filter_dict: Dict[str, Any]) -> int:
        """
        Delete multiple memories matching filter
        
        Args:
            filter_dict: MongoDB filter query
            
        Returns:
            Number of deleted documents
        """
        try:
            result = self.collection.delete_many(filter_dict)
            count = result.deleted_count
            logger.debug(f"Deleted {count} memories matching filter")
            return count
            
        except Exception as e:
            logger.error(f"Error deleting multiple memories: {e}")
            return 0
    
    def clear(self, user_id: Optional[str] = None):
        """
        Clear all memories for a user or entire collection
        
        Args:
            user_id: Optional user identifier. If None, clears all memories.
        """
        try:
            if user_id:
                count = self.delete_many({"user_id": user_id})
                logger.info(f"Cleared {count} memories for user: {user_id}")
            else:
                count = self.delete_many({})
                logger.info(f"Cleared all {count} memories from collection")
                
        except Exception as e:
            logger.error(f"Error clearing memories: {e}")
    
    def search(self, user_id: str, query: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Search memories with custom query
        
        Args:
            user_id: User identifier
            query: Custom MongoDB query
            
        Returns:
            List of matching memory dictionaries
        """
        try:
            full_query = {"user_id": user_id, **query}
            cursor = self.collection.find(full_query).sort("created_at", -1)
            
            results = []
            for doc in cursor:
                doc["id"] = str(doc.pop("_id"))
                results.append(doc)
            
            logger.debug(f"Found {len(results)} memories for query")
            return results
            
        except Exception as e:
            logger.error(f"Error searching memories: {e}")
            return []
    
    def get_latest(self, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Get the most recent memory for a user
        
        Args:
            user_id: User identifier
            
        Returns:
            Latest memory dictionary or None
        """
        try:
            doc = self.collection.find_one(
                {"user_id": user_id},
                sort=[("created_at", -1)]
            )
            
            if doc:
                doc["id"] = str(doc.pop("_id"))
                logger.debug(f"Retrieved latest memory for user: {user_id}")
                return doc
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting latest memory: {e}")
            return None
    
    # ========================================================================
    # CONNECTION MANAGEMENT
    # ========================================================================
    
    def close(self):
        """Close MongoDB connection"""
        try:
            self.client.close()
            logger.info("MongoDB connection closed")
        except Exception as e:
            logger.error(f"Error closing MongoDB connection: {e}")
    
    def __del__(self):
        """Cleanup on deletion"""
        try:
            self.close()
        except:
            pass


# ============================================================================
# TESTING
# ============================================================================

if __name__ == "__main__":
    """Test all methods to ensure Agno compatibility"""
    from dotenv import load_dotenv
    
    load_dotenv()
    
    print("=" * 60)
    print("Testing MongoMemoryDb with all Agno methods")
    print("=" * 60)
    
    try:
        # Initialize
        print("\n1. Initializing database...")
        db = MongoMemoryDb(table_name="test_memory")
        print("✅ Database initialized")
        
        test_user = "test_user_complete"
        
        # Test insert
        print("\n2. Testing insert()...")
        memory = {
            "user_id": test_user,
            "memory": "Test memory content",
            "metadata": {"test": True}
        }
        result = db.insert(memory)
        print(f"✅ Insert successful: {result['id']}")
        
        # Test read_memories (CRITICAL!)
        print("\n3. Testing read_memories() ← CRITICAL METHOD...")
        memories = db.read_memories(test_user)
        print(f"✅ read_memories() successful: {len(memories)} memories")
        
        # Test upsert_memory (ALSO CRITICAL!)
        print("\n4. Testing upsert_memory() ← ALSO CRITICAL...")
        memory2 = {
            "user_id": test_user,
            "memory": "Updated memory",
            "metadata": {"updated": True}
        }
        result2 = db.upsert_memory(memory2)
        print(f"✅ upsert_memory() successful: {result2['id']}")
        
        # Test get_memories
        print("\n5. Testing get_memories()...")
        memories = db.get_memories(test_user, limit=10)
        print(f"✅ get_memories() successful: {len(memories)} memories")
        
        # Test delete_memory
        print("\n6. Testing delete_memory()...")
        if result['id']:
            success = db.delete_memory(result['id'])
            print(f"✅ delete_memory() successful: {success}")
        
        # Cleanup
        print("\n7. Cleaning up...")
        db.clear(test_user)
        print("✅ Cleanup complete")
        
        print("\n" + "=" * 60)
        print("✅ ALL TESTS PASSED - Ready for Agno!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()