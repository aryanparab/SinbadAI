from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes import game
import os

app = FastAPI(title="Sinbad RPG Backend")

# ⭐ Add CORS middleware for frontend to connect
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your Vercel domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(game.router, prefix='/game')

# Root endpoint for health checks
@app.get("/")
async def root():
    return {"status": "healthy", "service": "Shadow Council API"}

# ⭐ CRITICAL: Bind to 0.0.0.0 for Render
if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)