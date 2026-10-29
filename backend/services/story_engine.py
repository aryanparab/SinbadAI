"""Narrative generation only. Campaign state and encounters are owned by game rules."""
import asyncio
import os
from pathlib import Path
from dotenv import load_dotenv
from groq import Groq
from prompts import build_director_instructions

load_dotenv(Path(__file__).resolve().parents[2] / '.env')
client = Groq(api_key=os.getenv('GROQ_API_KEY'), timeout=90, max_retries=0)

def generate(context):
    response = client.chat.completions.create(
        model=os.getenv('GROQ_MODEL', 'openai/gpt-oss-120b'),
        messages=[{'role': 'system', 'content': build_director_instructions()}, {'role': 'user', 'content': context}],
        response_format={'type': 'json_object'},
        max_tokens=8000,
        temperature=0.8,
    )
    content = response.choices[0].message.content
    if not content:
        raise ValueError('The narrative director returned no scene')
    return content

async def process_game_turn(player_input, user_id):
    return await asyncio.to_thread(generate, player_input)
