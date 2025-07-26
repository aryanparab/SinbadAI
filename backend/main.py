from fastapi import FastAPI
from routes import game

app = FastAPI(title="Sinbad RPG Backend")

app.include_router(game.router,prefix='/game')