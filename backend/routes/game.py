# routes.py
from fastapi import APIRouter, HTTPException, Request
from groq import RateLimitError
from services.story_engine import process_game_turn
from models.schemas import SceneResponse, AgentInput, UserInteraction, GameState, EnvironmentalConditions, ResourceAvailability, InventoryChanges, WorldInfo, CurrentSceneContext, GameProgressContext, LoreEntry, QuestObjective, Character, DialogueLine, InteractiveElement, EnvironmentalDiscovery, ThreatUpdate, AmbientEvent # Import all necessary Pydantic models
from agents.data_validate_game import parse_json_block, validate_and_fix_response
import logging
import json
from datetime import datetime
import os
from routes import campaign, encounters
from pydantic import BaseModel
import asyncio
import uuid
from collections import defaultdict
locks = defaultdict(asyncio.Lock)

from dotenv import load_dotenv

load_dotenv()

router = APIRouter()
logger = logging.getLogger(__name__)

def create_memory_data(input_data: AgentInput, scene_response: SceneResponse) -> dict:
    """Create memory data dictionary from input and scene response"""
    
    # Calculate updated inventory
    updated_inventory = [item.model_dump() for item in scene_response.current_inventory]
    
    # Create history entry
    history_entry = f"[{scene_response.location}] {scene_response.history_entry}"
    updated_history = (input_data.recent_history if input_data.recent_history else []) + [history_entry]
    
    # Keep only last 20 entries to prevent memory bloat
    if len(updated_history) > 20:
        updated_history = updated_history[-20:]
    
    # Use play_time_minutes and scenes_completed directly from input_data.game_progress
    play_time_minutes = input_data.game_progress.play_time_minutes
    scenes_completed = input_data.game_progress.scenes_completed
    
    # Extract discovered locations and met characters from existing memory and current scene
    existing_discovered_locations = input_data.current_scene.location_details.exits
    existing_met_characters = [char.id for char in input_data.current_scene.characters]

    discovered_locations = list(set(existing_discovered_locations + [scene_response.location]))
    met_characters = list(set(existing_met_characters + [char.id for char in scene_response.characters]))
    
    # Player choices history
    player_choices_history = input_data.game_progress.player_preferences.get('player_choices_history', []) + [{
        "scene_tag": scene_response.scene_tag,
        "location": scene_response.location,
        "choice": input_data.player_choice,
        "interaction_type": input_data.user_interaction.interaction_type,
        "timestamp": datetime.now().isoformat()
    }]

    # Lore collection
    lore_collection = input_data.current_scene.discovered_lore + scene_response.discovered_lore
    
    memory_data = {
        "session_id": input_data.session_id,
        "last_updated": datetime.now().isoformat(),
        "scene_tag": scene_response.scene_tag,
        "location": scene_response.location,
        "world": scene_response.world,
        "inventory": updated_inventory,
        "game_state": scene_response.game_state.model_dump(),
        "history": updated_history,

        "current_scene": {
            "narration_text": scene_response.narration_text,
            "dialogue": [dialogue.model_dump() for dialogue in scene_response.dialogue],
            "characters": [char.model_dump() for char in scene_response.characters],
            "options": scene_response.options,
            "mood_atmosphere": scene_response.mood_atmosphere,
            "relationship_changes": scene_response.relationship_changes,
            "new_secrets": scene_response.new_secrets,
            "interactive_elements": [element.model_dump() for element in scene_response.interactive_elements],
            "environmental_discoveries": [discovery.model_dump() for discovery in scene_response.environmental_discoveries],
            "threat_updates": [threat.model_dump() for threat in scene_response.threat_updates],
            "ambient_events": [event.model_dump() for event in scene_response.ambient_events],
            "discovered_lore": [lore.model_dump() for lore in scene_response.discovered_lore],
            "world_info": scene_response.world_info.model_dump(),
            "location_details": scene_response.location_details.model_dump()  # Convert to dict
        },

        "play_time_minutes": play_time_minutes,
        "scenes_completed": scenes_completed,
        
        "discovered_locations": discovered_locations,
        "met_characters": met_characters,
        "unlocked_features": input_data.game_progress.player_preferences.get('unlocked_features', []),
        
        "major_story_beats": input_data.game_progress.major_story_beats,
        "active_side_quests": input_data.game_progress.player_preferences.get('active_side_quests', []),
        "player_choices_history": player_choices_history,
        
        "world_knowledge": input_data.game_progress.world_knowledge,
        "faction_standings": input_data.game_progress.faction_standings,
        
        "discovered_secrets": list(set(input_data.game_state.revealed_secrets + scene_response.new_secrets)),
        "triggered_events": input_data.game_progress.player_preferences.get('triggered_events', []),
        
        "player_preferences": input_data.game_progress.player_preferences,
        
        "resume_context": {
            "last_user_interaction": input_data.user_interaction.model_dump(),
            "game_progress_context": input_data.game_progress.model_dump(),
            "recent_history": input_data.recent_history,
            "agent_hints": input_data.agent_hints,
            "emergency_flags": input_data.emergency_flags,
            "tension_level": input_data.game_progress.tension_level,
            "story_escalation_level": input_data.game_progress.story_escalation_level
        },
        "lore_collection": [lore.model_dump() for lore in lore_collection],
        "world_info": scene_response.world_info.model_dump()
    }
    
    return memory_data

def _get_interaction_specific_context(user_interaction: UserInteraction) -> str:
    """Generate context specific to the interaction type"""
    
    interaction_contexts = {
        "narrative_choice": "Player chose from narrative options - advance the main story flow",
        "character_interaction": f"Player is interacting with character {user_interaction.element_id} - focus on dialogue and relationship building",
        "item_interaction": f"Player is interacting with item {user_interaction.element_id} - focus on item mechanics and discovery",
        "location_interaction": f"Player is exploring location {user_interaction.element_id} - focus on environmental storytelling",
        "quest_interaction": f"Player is engaging with quest {user_interaction.element_id} - focus on objective progression",
        "environmental_interaction": f"Player is examining environment {user_interaction.element_id} - focus on world-building and atmosphere"
    }
    
    base_context = interaction_contexts.get(user_interaction.interaction_type, "Standard narrative progression")
    
    # Add additional context if available
    if user_interaction.interaction_context:
        context_details = ", ".join([f"{k}: {v}" for k, v in user_interaction.interaction_context.items()])
        base_context += f" (Additional context: {context_details})"
    
    return base_context

def create_game_context(input_data: AgentInput) -> str:
    """Create comprehensive game context string from enhanced AgentInput"""
    
    # Extract game state info safely
    game_state = input_data.game_state
    scenes_completed = input_data.game_progress.scenes_completed  # Fixed: use game_progress
    relationships = game_state.relationships
    revealed_secrets = game_state.revealed_secrets
    major_events = game_state.major_events
    active_objectives = game_state.active_objectives
    completed_objectives = game_state.completed_objectives
    story_flags = game_state.story_flags
    reputation = game_state.reputation
    
    # Format active objectives descriptions
    active_obj_descriptions = [obj.description for obj in active_objectives]
    
    # Format relationships for display
    relationship_display = {}
    for char_id, level in relationships.items():
        relationship_display[char_id] = f"{level}/10"
    
    # Extract user interaction details
    interaction_type = input_data.user_interaction.interaction_type
    choice_text = input_data.user_interaction.choice_text  # Fixed: use user_interaction
    element_info = ""
    if input_data.user_interaction.element_id:
        element_info = f" [Interacting with {input_data.user_interaction.element_type}: {input_data.user_interaction.element_id}]"
    
    # Extract current scene context
    current_scene = input_data.current_scene
    scene_mood = current_scene.mood_atmosphere
    scene_characters = [char.name for char in current_scene.characters]
    scene_interactive_elements = [elem.name for elem in current_scene.interactive_elements]
    scene_threats = [threat.threat_name for threat in current_scene.threat_updates]
    
    # Game progress context
    game_progress = input_data.game_progress
    escalation_level = game_progress.story_escalation_level
    tension_level = game_progress.tension_level
    
    # Previous scene narration — gives agents direct prose continuity reference
    prev_narration = current_scene.narration_text
    prev_narration_excerpt = (prev_narration[:600] + "…") if len(prev_narration) > 600 else prev_narration

    # Fixed: use consistent field names
    game_context = f"""
PLAYER INTERACTION CONTEXT:
Interaction Type: {interaction_type}
Player Choice: "{choice_text}"{element_info}
Previous Scene Tag: {input_data.scene_tag or "Game Start"}
Total Scenes Completed: {scenes_completed} (see campaign contract for total)

PREVIOUS SCENE NARRATION (maintain prose tone and continuity from this):
{prev_narration_excerpt}

CURRENT SCENE CONTEXT:
Location: {input_data.current_location}
World: {input_data.current_world}
Scene Mood: {scene_mood}
Present Characters: {input_data.present_characters}
Scene Characters: {scene_characters}
Interactive Elements: {scene_interactive_elements}
Active Threats: {scene_threats}
Discovered Lore: {[lore.title for lore in current_scene.discovered_lore]}
World Information: {current_scene.world_info.description} (Theme: {current_scene.world_info.theme})
Location Details: Exits: {current_scene.location_details.exits}, Safety: {current_scene.location_details.safety_level}/10

PLAYER STATE:
Current Inventory: {[item.name for item in input_data.current_inventory] if input_data.current_inventory else "Empty"}
Inventory Count: {len(input_data.current_inventory)}

GAME STATE CONTEXT:
- Character Relationships: {relationship_display or "None established"}
- Revealed Secrets: {revealed_secrets or "None"}
- Major Story Events: {major_events or "None"}
- Active Objectives: {active_obj_descriptions or "None"}
- Completed Objectives: {completed_objectives or "None"}
- Story Flags: {story_flags or "None"}
- Player Reputation: {reputation or "None"}
- Environmental Conditions: Weather: {game_state.environmental_conditions.weather}, Visibility: {game_state.environmental_conditions.visibility}, Temperature: {game_state.environmental_conditions.temperature}, Hazard: {game_state.environmental_conditions.hazard_level}/10
- Resource Availability: Food: {game_state.resource_availability.food}, Water: {game_state.resource_availability.water}, Medical: {game_state.resource_availability.medical_supplies}, Shelter: {game_state.resource_availability.shelter_materials}, Fuel: {game_state.resource_availability.fuel}, Tools: {game_state.resource_availability.tools}

STORY PROGRESSION:
- Scenes Completed: {scenes_completed}
- Play Time: {game_progress.play_time_minutes} minutes
- Story Escalation Level: {escalation_level}/10
- Tension Level: {tension_level}/10
- Major Story Beats: {game_progress.major_story_beats}
- Active Themes: {game_progress.active_themes}
- World Knowledge: {game_progress.world_knowledge}
- Faction Standings: {game_progress.faction_standings}
- Player Preferences: {game_progress.player_preferences}
- Preferred Interaction Types: {game_progress.preferred_interaction_types}

RECENT HISTORY CONTEXT:
{chr(10).join(input_data.recent_history) if input_data.recent_history else "This is the beginning of the adventure"}

CONTEXT: This is a continuation of an ongoing RPG session. Use the memory system to maintain continuity with past events, relationships, and character developments. The player has just made the choice: "{choice_text}" via {interaction_type}.

The player is currently in the world scenario: {input_data.current_world}

IMPORTANT NARRATIVE GUIDELINES:
- Maintain consistency with established relationships (current levels: {relationship_display})
- Reference and build upon revealed secrets: {revealed_secrets}
- Progress active objectives: {active_obj_descriptions}
- Acknowledge completed objectives: {completed_objectives}
- Characters should remember major events: {major_events}
- Respect story flags and player reputation: {story_flags} | {reputation}
- Present characters ({input_data.present_characters}) should act according to their relationship levels and memories
- Create meaningful consequences for player choices that affect future interactions
- Adjust story intensity based on escalation level ({escalation_level}/10) and tension level ({tension_level}/10)

INTERACTION-SPECIFIC HANDLING:
{_get_interaction_specific_context(input_data.user_interaction)}

SCENE REQUIREMENTS:
- Generate a scene_tag that reflects the current location and situation
- Include present characters in dialogue/interactions based on their relationship levels
- Update relationship levels based on player choice impact
- Add to major_events if this choice creates a significant story moment
- Progress or complete relevant objectives based on the player's action
- Maintain inventory consistency (current: {[item.name for item in input_data.current_inventory]})
- Create a meaningful history_entry summarizing what happens in this scene
- Respond appropriately to the {interaction_type} interaction type
- Ensure all fields in the SceneResponse schema are populated, even with empty lists/default values if no new data is generated.
- NARRATION CONTINUITY: The new narration_text must pick up tonally and contextually from the PREVIOUS SCENE NARRATION shown above. Do not restart world-building from scratch each scene.
- OPTIONS CONSISTENCY: Every option in the "options" array must directly relate to characters, events, or elements described in THIS scene's narration_text. No option should reference something not yet established.

Please coordinate your specialist agents to create a rich, interactive scene that responds to this player action while maintaining narrative continuity and advancing the story meaningfully.
"""
    
    return game_context

@router.post("/interact", response_model=SceneResponse)
async def interact(input: AgentInput):
    async with locks[input.session_id]:
        return await _interact(input)

async def _interact(input: AgentInput):
    """
    Main interaction endpoint for the RPG system
    """
    try:
        saved = campaign.load(input.session_id)
        if not saved:
            raise HTTPException(409, "Start a new campaign first.")
        previous = saved.get("memory")
        total = saved["total_turns"]
        completed = previous["scenes_completed"] if previous else 0
        if completed >= total:
            raise HTTPException(409, "This story is complete. Start a new adventure.")
        active_encounter = (previous or {}).get("game_state", {}).get("story_flags", {}).get("encounter")
        turn = completed + 1
        input.current_world = saved["world"]
        if previous:
            if input.scene_tag != previous["scene_tag"]:
                raise HTTPException(409, "This scene has already advanced. Reload to restore the latest turn.")
            input.current_inventory = previous["inventory"]
            input.game_state = previous["game_state"]
            input.current_location = previous["location"]
            input.scene_tag = previous["scene_tag"]
            current = dict(previous["current_scene"])
            current.update(scene_tag=previous["scene_tag"], location=previous["location"], world=previous["world"], narrative_options=current.pop("options"), new_objectives=[], completed_objectives_this_scene=[])
            input.current_scene = CurrentSceneContext(**current)
            input.recent_history = previous["history"]
        else:
            input.current_inventory = []
            input.game_state = GameState(
                relationships={}, revealed_secrets=[], completed_objectives=[], failed_objectives=[], active_objectives=[],
                location_flags={}, story_flags={}, reputation={}, major_events=[],
                environmental_conditions=EnvironmentalConditions(weather="clear", visibility="normal", temperature="comfortable", hazard_level=0),
                resource_availability=ResourceAvailability(food="unknown", water="unknown", medical_supplies="unknown", shelter_materials="unknown", fuel="unknown", tools="unknown"),
            )
            input.current_scene.characters = []
            input.current_scene.narration_text = ""
            input.current_location = "Opening scene"
            input.recent_history = []
        if input.user_interaction.element_type == "inventory_item":
            selected = next((i for i in input.current_inventory if i.name.casefold() == (input.user_interaction.element_id or "").casefold()), None)
            if not selected or selected.durability == 0:
                raise HTTPException(400, "That item is unavailable or broken.")
        if previous and input.user_interaction.element_type == "interactive_element":
            element = next((e for e in input.current_scene.interactive_elements if e.id == input.user_interaction.element_id), None)
            if not element:
                raise HTTPException(400, "That interaction is no longer available.")
            available = {i.name.casefold() for i in input.current_inventory if i.durability > 0}
            if any(name.casefold() not in available for name in element.requires_items):
                raise HTTPException(400, "You do not have the required items.")
        input.game_progress.scenes_completed = turn
        input.scenes_completed = turn
        plan = saved.get("plan", {})
        # Supply concise, authoritative continuity instead of a second creative prompt.
        game_context = json.dumps({
            "world": input.current_world, "location": input.current_location,
            "player_decision": input.player_choice,
            "previous_narration": input.current_scene.narration_text,
            "characters": [c.model_dump() for c in input.current_scene.characters],
            "state": input.game_state.model_dump(), "history": input.recent_history[-8:],
        }, ensure_ascii=False)
        game_context += f"""
CAMPAIGN CONTRACT (overrides generic pacing):
Turn {turn} of exactly {total}; phase: {campaign.phase(turn, total)}.
Each successful player approach consumes one story turn, including the opening. Resolve the attempted action in the narrative; never require abstract tactical progress.
If a legacy encounter is active, interpret the decision as an approach to THAT obstacle, not an aftermath choice. Resolve or materially transform it; do not repeat it unchanged.
Persistent outline: {json.dumps(plan)}
On the opening turn return story_plan with central_conflict, stakes, key_characters,
setup, midpoint_reversal, climax, and possible_endings. Plan the whole story before narrating.
Keep that outline across turns; adapt the outcome to actual player decisions and inventory.
Resolve the central conflict and show consequences ON turn {total}. No cliffhanger or new quest then.
On earlier turns do not end the campaign; bring existing threads toward the planned climax.
Inventory ledger is authoritative: {json.dumps([i.model_dump() for i in input.current_inventory])}
added_items quantities are gains; removed_items quantities are amounts consumed/lost;
modified_items change durability/properties only. Never remove an unowned item.
Return each item's full schema in every delta. current_inventory is computed by the server.
An item interaction must have a concrete consequence consistent with its description.
Only offer actions whose required items are available. Keep quests and relationships continuous.
An offered item is not an acquired item: add it only when this narration explicitly completes its acquisition.
Never offer to acquire an item already acquired this turn. Describe consumption and damage when applying their deltas.
Use relationship_changes as per-turn deltas; the server derives persistent relationship levels.
"""

        logger.info(
            f"Processing interaction | session={input.session_id} "
            f"scene={input.game_progress.scenes_completed} "
            f"location={input.current_location}"
        )
        logger.debug(f"Player choice: {input.player_choice}")

        for attempt in range(2):
            if not campaign.reserve_generation():
                raise HTTPException(429, "Today's demo generation limit has been reached. Your saved adventure and tactical encounters remain available.")
            raw_result_str = await process_game_turn(game_context, f"{input.session_id}:{saved.get('campaign_key', 'legacy')}")
            try:
                result_dict = parse_json_block(raw_result_str)
                if not isinstance(result_dict.get("narration_text"), str) or not isinstance(result_dict.get("options"), list):
                    raise ValueError("The director did not return a playable scene")
                result_dict = validate_and_fix_response(result_dict)
                scene_response = SceneResponse(**result_dict)
                if not plan and not all(scene_response.story_plan.get(key) for key in ("central_conflict", "climax", "possible_endings")):
                    raise ValueError("The opening must include a complete story_plan")
                break
            except ValueError:
                if attempt:
                    raise
                # One format repair is included in the shared daily quota.
                game_context += "\nFORMAT CORRECTION: Your previous response was not one valid scene object. Return exactly ONE JSON object with narration_text, options and all required scene fields. On the opening include story_plan with nonempty central_conflict, climax and possible_endings. Do not return a list, primitive, outline alone, or encoded JSON string. Keep the same world, action and story contract."

        if scene_response.scene_tag.startswith(("error", "fallback")):
            raise HTTPException(502, "The story engine could not generate a scene. Retry; your turn is unchanged.")
        if not plan:
            plan = scene_response.story_plan
            if not plan or not all(plan.get(k) for k in ("central_conflict", "climax", "possible_endings")):
                raise HTTPException(502, "The story engine did not return a complete campaign plan. Please retry.")
        if turn == total and not scene_response.ending_summary.strip():
            raise HTTPException(502, "The director did not finish the epilogue. Retry; your final turn is unchanged.")
        scene_response.scene_tag = f"turn_{turn}"
        scene_response.world = saved["world"]
        scene_response = campaign.reconcile(input, scene_response, turn, total, plan)
        # Prepare memory data
        memory_data = create_memory_data(input, scene_response)
        
        if previous:
            memory_data["lore_collection"] = list({entry["id"]: entry for entry in previous.get("lore_collection", []) + memory_data["lore_collection"]}.values())
            memory_data["discovered_locations"] = list(dict.fromkeys(previous.get("discovered_locations", []) + memory_data["discovered_locations"]))
            memory_data["met_characters"] = list(dict.fromkeys(previous.get("met_characters", []) + memory_data["met_characters"]))
            memory_data["player_choices_history"] = previous.get("player_choices_history", []) + memory_data["player_choices_history"][-1:]
        campaign.save(input.session_id, {**saved, "plan": plan, "memory": memory_data})
        logger.info(f"Successfully processed interaction for session {input.session_id}")
        scene_response.story_plan = {}
        scene_response.game_state.story_flags.pop("story_plan", None)
        return scene_response
        
    except HTTPException:
        raise
    except RateLimitError:
        logger.warning("AI provider rate limit reached; campaign progress unchanged")
        raise HTTPException(429, "The AI provider's free-tier limit was reached. Wait about a minute, then retry. Your saved progress is unchanged.", headers={"Retry-After": "60"})
    except ValueError as e:
        logger.error(f"JSON parsing error for session {input.session_id}: {e}", exc_info=True)
        raise HTTPException(status_code=502, detail="The generated scene was inconsistent. Please retry; no progress was changed.")
        
    except Exception as e:
        logger.error(f"Unexpected error for session {input.session_id}: {e}", exc_info=True)
        
        # Return a safe fallback response
        raise HTTPException(502, "The story engine is unavailable. Your progress is unchanged; please retry.")


class EncounterAction(BaseModel):
    session_id: str
    encounter_id: str
    expected_round: int
    action: str
    item_name: str = ""

@router.post("/encounter")
async def play_encounter(req: EncounterAction):
    async with locks[req.session_id]:
        saved = campaign.load(req.session_id)
        if not saved or not saved.get("memory"):
            raise HTTPException(404, "No campaign found.")
        snapshot = saved["memory"]
        flags = snapshot["game_state"]["story_flags"]
        encounter = flags.get("encounter")
        if not encounter or encounter["id"] != req.encounter_id:
            raise HTTPException(409, "This encounter is no longer available.")
        if encounter["round"] != req.expected_round:
            raise HTTPException(409, "This action was already resolved. Reload to see the result.")
        try:
            encounter, inventory = encounters.resolve(encounter, req.action, snapshot["inventory"], req.item_name)
        except ValueError as exc:
            raise HTTPException(400, str(exc))
        snapshot["inventory"] = inventory
        flags["encounter"] = encounter
        snapshot["scene_tag"] = f"turn_{snapshot['scenes_completed']}_enc_{encounter['round']}"
        snapshot["last_updated"] = datetime.now().isoformat()
        if encounter["status"] != "active":
            outcome = {"id": encounter["id"], "title": encounter["title"], "status": encounter["status"], "health": encounter["health"], "reward_claimed": encounter["reward_claimed"]}
            flags["encounter_history"] = flags.get("encounter_history", []) + [outcome]
            snapshot["history"] = (snapshot["history"] + [f"Encounter {encounter['title']}: {encounter['status']}. {encounter['log'][-1]}"])[-20:]
        campaign.save(req.session_id, saved)
        return {"memory": snapshot}


@router.post("/init")
async def init_game(request: Request):
    """
    Initialize or load a game session
    """
    body = await request.json()
    session_id = body.get("session_id")
    action = body.get("action")
    world = body.get("world", "default")


    if not isinstance(session_id, str) or not session_id or len(session_id) > 200:
        raise HTTPException(400, "A valid session ID is required.")
    if action == "new":
        total = body.get("total_turns", 30)
        if type(total) is not int or not 5 <= total <= 60:
            raise HTTPException(400, "Choose 5 to 60 turns.")
        if not isinstance(world, str) or not world.strip() or len(world) > 1200:
            raise HTTPException(400, "Enter a world name of at most 1200 characters.")
        async with locks[session_id]:
            campaign.save(session_id, {"world": world.strip(), "total_turns": total, "campaign_key": str(uuid.uuid4()), "plan": {}, "memory": None})
        return {"status": "cleared", "world": world.strip(), "total_turns": total}
    elif action == "load":
        saved = campaign.load(session_id)
        if saved and saved.get("memory"):
            return {"status": "loaded", "latest_memory_data": saved["memory"], "scene_state": saved["memory"]["current_scene"]["narration_text"]}
        return {"status": "no_memory"}

    raise HTTPException(400, "Invalid action. Use new or load.")


@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "engine": "ready"}
