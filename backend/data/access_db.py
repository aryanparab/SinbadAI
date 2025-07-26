from agno.memory.v2.db.sqlite import SqliteMemoryDb
from agno.memory.v2.memory import Memory

import os
from dotenv import load_dotenv

load_dotenv()

db_file = "data/agent_memory.db"
session_id = "sakurawave1311@gmail.com"

# Create memory with persistent storage
memory_db = SqliteMemoryDb(table_name="game_memory", db_file=db_file)
memory = Memory(db=memory_db)
print(memory)
memory_db.clear()