from agno.agent import Agent
from agno.models.google.gemini import Gemini
from agno.models.groq import Groq
from agno.memory.v2.db.sqlite import SqliteMemoryDb
from agno.memory.v2.memory import Memory
from agno.team import Team
from dotenv import load_dotenv
import os
import asyncio
import json
from data.storage import get_memory_db

# Import Pydantic models
from models.schemas import (
    SceneResponse, AgentInput, Item, DialogueLine, Character, QuestObjective,
    EnvironmentalConditions, ResourceAvailability, GameState, InteractiveElement,
    EnvironmentalDiscovery, ThreatUpdate, AmbientEvent, LoreEntry, WorldInfo,
    UserInteraction, CurrentSceneContext, GameProgressContext, InventoryChanges
)

load_dotenv()

memory_db = get_memory_db()




# Initialize models
try:
    gemini_model = Gemini(
   "gemini-2.0-flash",
    api_key=os.getenv("GEMINI_API_KEY")
)
    
    groq_model = Groq(
        "gemma2-9b-it",
        api_key=os.getenv("GROQ_API_KEY")
    )
except Exception as e:
    print(f"Error initializing models: {e}")
    exit(1)

# Setup Memory
# memory = Memory(
#     model=gemini_model,
#     db=SqliteMemoryDb(table_name="game_memory", db_file=db_file)
# )
memory = Memory( model=gemini_model,db=memory_db)
# OPTIMIZED AGENTS - STREAMLINED FOR EFFICIENCY

narrative_tool = Agent(
    name="narrative_agent",
    model=groq_model,
    instructions="""Create cinematic 400-600 word scene descriptions for movie-like experience.
MOVIE FOCUS: Each scene is a crucial story beat - opening, rising action, climax, resolution.
PACING: Scenes 1-10 (setup/world-building), 11-25 (rising tension), 26-40 (climax), 41-50 (resolution/ending).
STYLE: Cinematic present tense, rich sensory details, emotional depth, cliffhanger momentum.
STORY PROGRESSION: Each scene must advance plot significantly - major revelations, character development, world changes.
ENDING PREPARATION: Scenes 40+ should build toward meaningful conclusion with character arcs completing.
AVOID: Trivial interactions, simple movements, basic conversations.
INCLUDE: High stakes moments, emotional beats, plot revelations, character growth.
OUTPUT: narration_text (600-800 words) with cinematic tension and major story advancement."""
)

npc_agent = Agent(
    name="npc_agent",
    model=groq_model,
    instructions="""Create deep, evolving NPCs with significant story impact and meaningful relationships.
CHARACTER DEPTH: Each NPC has complex motivations, secrets, character arcs, and story importance.
RELATIONSHIP EVOLUTION: Trust/relationship changes should be dramatic based on major story events.
STORY ROLES: NPCs drive plot forward - allies become enemies, reveal secrets, make sacrifices, betray player.
DIALOGUE FOCUS: NPCs speak with purpose - reveal plot, show personality, create conflict, advance story.
AVOID: Small talk, trivial interactions, surface-level conversations.
INCLUDE: Emotional revelations, plot-critical information, character backstory, moral conflicts.
ENDING ARCS: Characters should have meaningful resolutions - redemption, sacrifice, revelation, growth.
OUTPUT: Complete character data with dramatic relationship changes and story-driving interactions."""
)

world_tool = Agent(
    name="worldbuilder_agent",
    model=groq_model,
    instructions="""Design evolving locations and interactive elements that respond to story progression.
WORLD EVOLUTION: World changes based on scenes completed (1-50) - settlements grow, threats spread, resources shift.
CREATE: Environmental details, weather patterns, hazards, discoverable objects, hidden areas, resource nodes.
FILL: location_flags, environmental_conditions, resource_availability, world_info (complete with key_locations, dominant_factions, major_threats, cultural_notes, historical_timeline), location_details (exits, hidden_areas, resource_nodes, safety_level).
PROGRESSION: Early scenes = basic survival, mid scenes = faction conflicts, late scenes = world-changing events.
OUTPUT: Complete world state with all location and environmental data filled."""
)

threat_agent = Agent(
    name="threat_agent",
    model=groq_model,
    instructions="""Create ACTIVE, PHYSICALLY ENGAGING threats that directly attack/interact with player and NPCs.
ACTIVE ENGAGEMENT: Threats don't just exist - they ACT. "Zombie grabs your arm", "Raptor pounces on Sarah", "Raider shoots at cover", "Beast drags wounded ally away".
PHYSICAL INTERACTION: Threats grab, chase, corner, wound, kill, trap, hunt, ambush, stalk.
NPC IMPACT: Threats actively target NPCs - wound them, kill them, capture them, threaten them.
ESCALATION: Early threats injure/scare, mid-game threats kill NPCs, late-game threats are lethal boss encounters.
CONSEQUENCES: Threat actions have immediate story impact - injured allies, dead characters, changed dynamics.
RESOLUTION VARIETY: Combat, stealth, sacrifice, negotiation, environmental solutions.
MOVIE MOMENTS: Create scenes like "alien bursts from chest", "T-Rex breaks fence", "zombies swarm".
OUTPUT: Immediate, physical threat interactions that create dramatic story moments and force crucial decisions."""
)

quest_agent = Agent(
    name="quest_agent",
    model=groq_model,
    instructions="""Create story-critical objectives that drive the 50-scene narrative toward meaningful conclusion.
STORY ARCS: Early quests establish world/survival, mid-game reveals larger plot, end-game resolves everything.
MEANINGFUL OBJECTIVES: Each quest should advance main story significantly - not fetch quests or busy work.
CHARACTER INTEGRATION: Quests involve NPCs deeply - their fates, secrets, character arcs.
ENDING PREPARATION: Final quests should offer multiple resolution paths and character arc conclusions.
OBJECTIVE TYPES: Rescue operations, moral choices, survival decisions, story revelations, character confrontations.
AVOID: Collect items, explore areas, basic survival tasks unless story-critical.
INCLUDE: Character-driven goals, plot revelations, moral dilemmas, world-changing decisions.
OUTPUT: Story-critical objectives that create dramatic moments and advance toward meaningful ending."""
)

emotion_agent = Agent(
    name="emotion_agent",
    model=groq_model,
    instructions="""Track complex emotional states and evolving relationships.
EMOTIONAL DEPTH: Characters react to major events, remember past interactions, hold grudges, form bonds.
RELATIONSHIP EVOLUTION: Trust builds/breaks based on player choices and story events.
MOOD DYNAMICS: Fear, hope, desperation, triumph - emotions should match story intensity.
FILL: relationship_changes with clear numerical impacts, current_mood updates.
GROUP DYNAMICS: How characters interact with each other, not just player.
OUTPUT: Detailed relationship changes and emotional consequences."""
)

event_agent = Agent(
    name="event_agent",
    model=groq_model,
    instructions="""Generate cinematic ambient events that enhance story atmosphere.
EVENT TYPES: Environmental (storm approaches, ground shakes), interpersonal (arguments, revelations), discovery (hidden passages, messages), tension (sounds, movements).
STORY RELEVANCE: Events should foreshadow major plot points or reveal world lore.
FILL: event_type, description, affects_mood, creates_opportunities.
CINEMATIC TIMING: Events should build tension and create story moments.
OUTPUT: Atmospheric events that enhance narrative immersion."""
)

item_agent = Agent(
    name="item_agent",
    model=groq_model,
    instructions="""Manage meaningful items that serve story and survival purposes.
ITEM TYPES: survival (food, water, medicine), tools (weapons, equipment), information (journals, keys), plot items (artifacts, evidence).
FILL: name, quantity, description, durability (0-100), item_type, properties with detailed information.
STORY INTEGRATION: Items should connect to quests, character backstories, world lore.
INVENTORY TRACKING: Track added_items, removed_items, modified_items with clear reasons.
OUTPUT: Complete item data with story significance and mechanical function."""
)

structure_agent = Agent(
    name="structure_agent",
    model=groq_model,
    instructions="""Create interactive structures that serve story and gameplay.
STRUCTURE TYPES: shelters (temporary safety), functional buildings (crafting, storage), ruins (lore, danger), natural formations (caves, trees).
STORY INTEGRATION: Structures should reflect world evolution and story progression.
FILL: All interactive_elements fields (id, name, description, interaction_types, requires_items, unlocks_options, options, potential_outcomes, side_quest_trigger).
FUNCTIONALITY: Structures should offer meaningful choices and consequences.
OUTPUT: Complete structure data with interaction options and story connections."""
)

lore_agent = Agent(
    name="lore_agent",
    model=groq_model,
    instructions="""Discover and manage deep world lore that enhances story immersion.
LORE CATEGORIES: history (world events), character (backstories), location (secrets), faction (politics), event (major incidents), artifact (mysterious items).
FILL: id, title, content, category, discovered_at (ISO datetime), related_entries, importance_level (1-10).
STORY INTEGRATION: Lore should explain world state, character motivations, and foreshadow future events.
CONSISTENCY: Maintain world logic and connection between lore entries.
OUTPUT: Rich lore entries that deepen world understanding and story engagement."""
)

choice_agent = Agent(
    name="choice_agent",
    model=groq_model,
    instructions="""Create 3-4 MAJOR decision points that significantly impact story, characters, and world.
MAJOR DECISIONS ONLY: Life/death choices, moral dilemmas, story-changing actions, character fate decisions.
AVOID: Simple movement, basic actions, trivial choices like "look around" or "talk to NPC".
STORY IMPACT: Each choice should have major consequences - character deaths, story branches, world changes.
MORAL WEIGHT: Choices involve sacrifice, betrayal, heroism, survival ethics, character loyalty.
EXAMPLES: "Save ally or escape", "Trust betrayer or go alone", "Sacrifice self or let others die", "Reveal secret or protect someone".
ENDING CHOICES: Final scenes should offer meaningful resolutions - redemption, sacrifice, different ending paths.
CONSEQUENCE CLARITY: Players should understand the weight and potential outcomes of their choices.
OUTPUT: 3-4 crucial decisions that drive story forward and create meaningful consequences."""
)
dialogue_agent = Agent(
    name="dialogue_agent",
    model=groq_model,
    instructions="""Generate substantial, story-driving dialogue that advances plot and reveals character.
DIALOGUE DEPTH: 5-6 meaningful exchanges per scene, each revealing plot/character information.
STORY ADVANCEMENT: Every dialogue exchange should reveal secrets, advance plot, show character growth, or create conflict.
EMOTIONAL WEIGHT: Dialogue carries emotional impact - confessions, arguments, revelations, farewells.
AVOID: Small talk, pleasantries, trivial exchanges, exposition dumps.
INCLUDE: Character secrets, plot revelations, emotional conflicts, backstory, moral dilemmas.
SCENE IMPACT: Dialogue should change relationships, reveal information, create new objectives.
ENDING PREPARATION: Late-game dialogue resolves character arcs, reveals final secrets, provides closure.
OUTPUT: Rich dialogue array with substantial story progression and character development."""
)


# OPTIMIZED ORCHESTRATOR - REDUCED VERBOSITY



orchestrator_agent = Agent(
    name="orchestrator_agent",
    model=gemini_model,
    tools=[
        narrative_tool, world_tool, npc_agent, threat_agent, quest_agent,
        emotion_agent, event_agent, item_agent, structure_agent, lore_agent,
        choice_agent, dialogue_agent
    ],
    memory=memory,
    instructions="""Create cinematic survival RPG with movie-like pacing and meaningful 50-scene story arc.
The name of the Player is : Sinbad (ALWAYS REFER PLAYER BY THIS NAME.)
Always Keep the Scenes Compleleted in the input accoutable and progress the story.
MOVIE STRUCTURE:
- Scenes 1-10: Setup (world introduction, character establishment, inciting incident)
- Scenes 11-25: Rising Action (conflicts escalate, relationships develop, stakes raise)
- Scenes 26-40: Climax (major confrontations, revelations, character moments)
- Scenes 41-50: Resolution (character arcs conclude, meaningful endings, story closure)

CINEMATIC REQUIREMENTS:
- Rich 400-600 word narration per scene
- Substantial dialogue that drives story forward
- Major decision points only - no trivial choices
- Active threats that physically engage characters
- Meaningful character development and relationships
- Story progression that builds toward satisfying conclusion

THREAT ENGAGEMENT: Threats must actively interact - attack, grab, chase, wound, kill NPCs and threaten player directly.

ENDING FOCUS: Final scenes must provide meaningful resolution to character arcs and story threads.

ESCAPE QUOTES: Use \" for internal quotes in JSON strings.

PROCESS:
1. Call all 12 tools with enhanced input
2. Synthesize into complete scene
3. Return ONLY valid JSON matching SceneResponse schema

CRITICAL VALIDATION:
- narration_text: 200-2000 chars
- history_entry: 50-500 chars  
- options: 2-6 items max
- relationship_level/trust_level: -10 to 10
- durability: 0-100
- hazard_level: 0-10
- escalation_level: 1-10
- progress: 0-100
- safety_level: 1-10
- importance_level: 1-10
- discovered_at: ISO datetime string
- category: 'history'|'character'|'location'|'faction'|'event'|'artifact'

NULL HANDLING:
- Use null for missing optional fields, never empty strings/objects
- Required fields must have valid values
- Arrays can be empty [] but not null
- Objects can be empty {} but not null if required

JSON STRUCTURE (exact match to SceneResponse):
```json
{
  "scene_tag": "string",
  "location": "string", 
  "world": "string",
  "narration_text": "string (200-2000 chars)",
  "dialogue": [
    {
      "speaker": "string",
      "text": "string", 
      "emotion": "string",
      "is_internal_thought": boolean,
      "audible_to": ["string"]
    }
  ],
  "characters": [
    {
      "id": "string",
      "name": "string",
      "avatar": "string",
      "interactable": boolean,
      "relationship_level": integer (-10 to 10),
      "current_mood": "string",
      "trust_level": integer (-10 to 10),
      "memories": ["string"],
      "personal_objectives": ["string"],
      "knowledge_flags": {"key": boolean},
      "backstory": "string or null",
      "faction": "string or null", 
      "skills": ["string"] or null,
      "equipment": ["string"] or null
    }
  ],
  "options": ["string"] (2-6 items),
  "game_state": {
    "relationships": {"char_id": integer},
    "revealed_secrets": ["string"],
    "completed_objectives": ["string"],
    "failed_objectives": ["string"],
    "active_objectives": [
      {
        "id": "string",
        "description": "string",
        "quest_type": "string",
        "completed": boolean,
        "involves_npcs": ["string"],
        "progress": integer (0-100),
        "escalation_level": integer (1-10),
        "rewards": ["string"] or null,
        "time_limit": "string or null"
      }
    ],
    "location_flags": {"key": boolean},
    "story_flags": {"key": "value"},
    "reputation": {"faction": "status"},
    "major_events": ["string"],
    "environmental_conditions": {
      "weather": "string",
      "visibility": "string", 
      "temperature": "string",
      "hazard_level": integer (0-10)
    },
    "resource_availability": {
      "food": "string",
      "water": "string",
      "medical_supplies": "string",
      "shelter_materials": "string",
      "fuel": "string",
      "tools": "string"
    }
  },
  "inventory_changes": {
    "added_items": [
      {
        "name": "string",
        "quantity": integer,
        "description": "string",
        "durability": integer (0-100),
        "item_type": "string",
        "properties": {"key": "value"}
      }
    ],
    "removed_items": [...],
    "modified_items": [...]
  },
  "current_inventory": [...],
  "mood_atmosphere": "string",
  "history_entry": "string (50-500 chars)",
  "relationship_changes": {"char_id": integer},
  "new_secrets": ["string"],
  "new_objectives": [...],
  "completed_objectives_this_scene": ["string"],
  "interactive_elements": [
    {
      "id": "string",
      "name": "string", 
      "description": "string",
      "interaction_types": ["string"],
      "requires_items": ["string"],
      "unlocks_options": ["string"],
      "options": ["string"],
      "potential_outcomes": {"key": "value"},
      "side_quest_trigger": {"key": "value"} or null
    }
  ],
  "environmental_discoveries": [
    {
      "name": "string",
      "description": "string",
      "significance": "string", 
      "unlocks_content": ["string"]
    }
  ],
  "threat_updates": [
    {
      "threat_id": "string",
      "threat_name": "string",
      "escalation_level": integer (1-10),
      "immediate_danger": boolean,
      "resolution_methods": ["string"],
      "affects_npcs": ["string"]
    }
  ],
  "ambient_events": [
    {
      "event_type": "string",
      "description": "string",
      "affects_mood": boolean,
      "creates_opportunities": ["string"]
    }
  ],
  "discovered_lore": [
    {
      "id": "string",
      "title": "string",
      "content": "string",
      "category": "history|character|location|faction|event|artifact",
      "discovered_at": "ISO datetime string",
      "related_entries": ["string"],
      "importance_level": integer (1-10)
    }
  ],
  "world_info": {
    "name": "string",
    "theme": "string",
    "description": "string",
    "key_locations": ["string"],
    "dominant_factions": ["string"], 
    "major_threats": ["string"],
    "cultural_notes": ["string"],
    "historical_timeline": [{"period": ["events"]}]
  },
  "location_details": {
    "exits": ["string"],
    "hidden_areas": ["string"],
    "resource_nodes": ["string"],
    "safety_level": integer (1-10)
  }
}
```

FIELD MAPPING:
- narrative_tool → narration_text
- npc_agent + emotion_agent → characters + relationship_changes  
- quest_agent → new_objectives + active_objectives
- dialogue_agent → dialogue
- choice_agent → options
- world_tool → environmental_conditions + resource_availability + world_info + location_details
- threat_agent → threat_updates
- event_agent → ambient_events
- item_agent → inventory_changes + current_inventory
- lore_agent → discovered_lore
- structure_agent → interactive_elements

OUTPUT: Only valid JSON in ```json blocks. All fields must be populated with appropriate values or null where optional. Ensure cinematic, story-driven scenes with meaningful progression."""
)

# Streamlined usage function
async def process_game_turn(player_input: AgentInput, user_id: str) -> str: # Changed return type to str
    
    """Process player turn and return game response"""
    try:
        final_response_str = orchestrator_agent.run(player_input, user_id=user_id)
        # Return the JSON string directly as per user's request
        return final_response_str.content
    except Exception as e:
        print(f"Error in process_game_turn: {e}")
        # Default WorldInfo for error response
        default_world_info = WorldInfo(
            name="Unknown World",
            theme="Uncertainty",
            description="A world shrouded in error.",
            key_locations=[],
            dominant_factions=[],
            major_threats=[],
            cultural_notes=[],
            historical_timeline=[]
        )
        # Default LocationDetails for error response
        default_location_details = {
            "exits": [],
            "hidden_areas": [],
            "resource_nodes": [],
            "safety_level": 5
        }

        # Return a JSON string for the error response
        error_response_dict = {
            "scene_tag": "error_scene",
            "location": "unknown",
            "world": "unknown",
            "narration_text": "The world shimmers momentarily, an error disrupting the fabric of reality. Please try again.",
            "dialogue": [],
            "characters": [],
            "options":["Continue", "Look around", "Check inventory"],
            "game_state": {
                "relationships": {},
                "revealed_secrets": [],
                "completed_objectives": [],
                "failed_objectives": [],
                "active_objectives": [],
                "location_flags": {},
                "story_flags": {},
                "reputation": {},
                "major_events": [],
                "environmental_conditions": EnvironmentalConditions().model_dump(), # Use model_dump()
                "resource_availability": ResourceAvailability().model_dump() # Use model_dump()
            },
            "inventory_changes": InventoryChanges().model_dump(), # Use model_dump()
            "current_inventory": [],
            "mood_atmosphere": "uncertain",
            "history_entry": "An unexpected pause occurred due to an error.",
            "relationship_changes": {},
            "new_secrets": [],
            "new_objectives": [],
            "completed_objectives_this_scene": [],
            "interactive_elements": [],
            "environmental_discoveries": [],
            "threat_updates": [],
            "ambient_events": [],
            "discovered_lore": [],
            "world_info": default_world_info.model_dump(), # Use model_dump()
            "location_details": default_location_details
        }
        return json.dumps(error_response_dict)