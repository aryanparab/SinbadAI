FROM python:3.12-slim
WORKDIR /app
ENV PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1 CAMPAIGN_DB_PATH=/app/data/campaigns.sqlite3
COPY requirements.lock .
RUN pip install --no-cache-dir --upgrade pip==26.2.2 && pip install --no-cache-dir -r requirements.lock
COPY main.py .
COPY models ./models
COPY routes ./routes
COPY prompts ./prompts
COPY services ./services
COPY agents/data_validate_game.py ./agents/data_validate_game.py
RUN mkdir -p /app/data
EXPOSE 8000
CMD ["sh", "-c", "exec uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000} --workers 1"]
