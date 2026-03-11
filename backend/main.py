from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes import game
import os

app = FastAPI(title="Sinbad RPG Backend")

# CORS — set ALLOWED_ORIGINS env var to comma-separated list of allowed frontend origins.
# e.g. ALLOWED_ORIGINS=https://yourapp.vercel.app,https://www.yourdomain.com
# Falls back to wildcard only in non-production so local dev still works.
_raw_origins = os.getenv("ALLOWED_ORIGINS", "")
if _raw_origins:
    allow_origins = [o.strip() for o in _raw_origins.split(",") if o.strip()]
    allow_credentials = True
else:
    # No origins configured — open wildcard (dev only; credentials disabled per CORS spec)
    allow_origins = ["*"]
    allow_credentials = False

app.add_middleware(
    CORSMiddleware,
    allow_origins=allow_origins,
    allow_credentials=allow_credentials,
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