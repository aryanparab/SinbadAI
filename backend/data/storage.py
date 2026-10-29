"""
Storage selector for Shadow Council / Sinbad AI
Automatically chooses between SQLite (dev) and MongoDB (production)
Uses unified wrapper for consistent interface
"""

import os
import logging
from typing import Union
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_memory_db():
    """
    Return appropriate memory database based on environment
    Wrapped in UnifiedMemoryDb for consistent interface
    
    Returns:
        UnifiedMemoryDb instance wrapping either SQLite or MongoDB
    """
    environment = os.getenv("ENVIRONMENT", "development")
    
    logger.info(f"🔧 Environment: {environment}")
    
    if environment == "production":
        # Production: Try MongoDB first
        logger.info("📊 Using MongoDB for memory storage")
        
        mongodb_uri = os.getenv("MONGODB_URI")
        if not mongodb_uri:
            logger.error("❌ MONGODB_URI not set! Falling back to SQLite")
            logger.warning("⚠️ Set MONGODB_URI in your environment variables for production")
            return _get_sqlite_db()
        
        try:
            from data.mongo_memory import MongoMemoryDb
            from data.unified_memory_wrapper import UnifiedMemoryDb
            
            db = MongoMemoryDb(table_name="game_memory")
            wrapped_db = UnifiedMemoryDb(db)
            logger.info("✅ MongoDB memory database initialized (wrapped)")
            return wrapped_db
            
        except ImportError as e:
            logger.error(f"❌ Failed to import MongoDB modules: {e}")
            logger.info("💡 Make sure mongo_memory.py and unified_memory_wrapper.py are in the same directory")
            logger.warning("⚠️ Falling back to SQLite")
            return _get_sqlite_db()
        except Exception as e:
            logger.error(f"❌ Failed to initialize MongoDB: {e}")
            logger.warning("⚠️ Falling back to SQLite")
            return _get_sqlite_db()
    else:
        # Development: Use SQLite
        return _get_sqlite_db()

def _get_sqlite_db():
    """Helper function to get SQLite database with unified wrapper"""
    logger.info("📂 Using SQLite for memory storage")
    
    try:
        from agno.memory.v2.db.sqlite import SqliteMemoryDb
        from data.unified_memory_wrapper import UnifiedMemoryDb
        
        # Ensure data directory exists
        data_dir = "data"
        os.makedirs(data_dir, exist_ok=True)
        
        db_file = os.getenv("AGENT_DB_PATH", os.path.join(data_dir, "agent_context.sqlite3"))
        db = SqliteMemoryDb(
            table_name="game_memory", 
            db_file=db_file
        )
        
        wrapped_db = UnifiedMemoryDb(db)
        logger.info(f"✅ SQLite memory database initialized at: {db_file} (wrapped)")
        return wrapped_db
        
    except ImportError as e:
        logger.error(f"❌ Failed to import SqliteMemoryDb: {e}")
        logger.error("💡 Make sure agno is installed: pip install agno")
        raise
    except Exception as e:
        logger.error(f"❌ Failed to initialize SQLite: {e}")
        raise

def test_memory_connection():
    """
    Test memory database connection with unified interface
    Returns True if successful, False otherwise
    """
    try:
        logger.info("🧪 Testing memory database connection...")
        db = get_memory_db()
        
        logger.info(f"📊 Database type: {db.db_type}")
        
        # Try a simple operation using unified interface
        test_data = {
            "user_id": "test_user",
            "memory": "test_memory"
        }
        
        # Insert test data
        result = db.insert(test_data)
        logger.info(f"✅ Test insert successful")
        
        # Try to retrieve
        all_data = db.select_all(user_id="test_user")
        logger.info(f"✅ Retrieved {len(all_data)} test records")
        
        # Clean up test data
        db.clear(user_id="test_user")
        logger.info("✅ Test cleanup successful")
        
        logger.info("✅ Memory database connection test passed")
        return True
        
    except Exception as e:
        logger.error(f"❌ Memory database connection test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

# Optional: Auto-test on import in development
if __name__ == "__main__":
    test_memory_connection()