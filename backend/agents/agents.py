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
import logging
from data.storage import get_memory_db
from prompts import build_director_instructions

logger = logging.getLogger(__name__)

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
        os.getenv("GROQ_MODEL", "openai/gpt-oss-120b"),
        api_key=os.getenv("GROQ_API_KEY"),
        request_params={"response_format": {"type": "json_object"}},
        max_tokens=12000,
        timeout=90,
        max_retries=0
    )
except Exception as e:
    logger.critical(f"Failed to initialize AI models: {e}", exc_info=True)
    raise RuntimeError(f"AI model initialization failed: {e}") from e

# Setup Memory
# memory = Memory(
#     model=gemini_model,
#     db=SqliteMemoryDb(table_name="game_memory", db_file=db_file)
# )
memory = Memory( model=groq_model,db=memory_db)
# OPTIMIZED AGENTS - STREAMLINED FOR EFFICIENCY

narrative_tool = Agent(
    name="narrative_agent",
    model=groq_model,
    instructions="""Create cinematic 100-220 word scene descriptions for movie-like experience.
MOVIE FOCUS: Each scene is a crucial story beat - opening, rising action, climax, resolution.
PACING: Use the supplied campaign phase and turn budget; final turn is resolution.
STYLE: Cinematic present tense, rich sensory details, emotional depth, cliffhanger momentum.
STORY PROGRESSION: Each scene must advance plot significantly - major revelations, character development, world changes.
ENDING PREPARATION: The final 20% of turns should build toward meaningful conclusion with character arcs completing.
AVOID: Trivial interactions, simple movements, basic conversations.
INCLUDE: High stakes moments, emotional beats, plot revelations, character growth.
CRITICAL: Keep output to 100-220 words maximum. Do NOT exceed this — the text must fit within 1800 characters.
OUTPUT: narration_text (100-220 words) with cinematic tension and major story advancement."""
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
WORLD EVOLUTION: World changes based on scenes completed (within the campaign turn budget) - settlements grow, threats spread, resources shift.
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
    instructions="""Create story-critical objectives that drive the bounded narrative toward meaningful conclusion.
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
CRITICAL: All options MUST directly follow from what is described in the current scene's narration and situation. Options that reference characters, places, or events not yet established in this scene will confuse the player.
OUTPUT: 3-4 crucial decisions as SHORT action phrases (5-12 words each) that drive story forward and create meaningful consequences."""
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
    telemetry=False,
    model=groq_model,
    tools=[
        narrative_tool, world_tool, npc_agent, threat_agent, quest_agent,
        emotion_agent, event_agent, item_agent, structure_agent, lore_agent,
        choice_agent, dialogue_agent
    ],
    memory=memory,
    instructions=build_director_instructions()
)

# Streamlined usage function
async def process_game_turn(player_input: str, user_id: str) -> str:
    """Process player turn and return game response.

    orchestrator_agent.run() is a synchronous blocking call (Agno doesn't yet
    expose a native async run). We offload it to a thread via asyncio.to_thread
    so the FastAPI event loop is not blocked while waiting for the LLM response.
    """
    try:
        final_response_str = await asyncio.to_thread(
            orchestrator_agent.run, player_input, user_id=user_id
        )
        logger.debug(f"Raw agent response length: {len(final_response_str.content)}")
        return final_response_str.content
    except Exception:
        logger.exception("Story generation failed")
        raise
