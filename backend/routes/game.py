# routes.py
from fastapi import APIRouter, HTTPException, Request
from agents.agents import process_game_turn, memory
from models.schemas import SceneResponse, AgentInput, UserInteraction, GameState, EnvironmentalConditions, ResourceAvailability, InventoryChanges, WorldInfo, CurrentSceneContext, GameProgressContext, LoreEntry, QuestObjective, Character, DialogueLine, InteractiveElement, EnvironmentalDiscovery, ThreatUpdate, AmbientEvent # Import all necessary Pydantic models
from agents.data_validate_game import parse_json_block, validate_and_fix_response
from routes.memory_service import (
    add_game_memory, 
    get_user_memories, 
    clear_user_memories, 
    get_memory_summary
)
import logging
import json
from datetime import datetime

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
    
    # Fixed: use consistent field names
    game_context = f"""
PLAYER INTERACTION CONTEXT:
Interaction Type: {interaction_type}
Player Choice: "{choice_text}"{element_info}
Previous Scene Tag: {input_data.scene_tag or "Game Start"}
Total Scenes Completed: {scenes_completed} out of 50

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

Please coordinate your specialist agents to create a rich, interactive scene that responds to this player action while maintaining narrative continuity and advancing the story meaningfully.
"""
    
    return game_context

@router.post("/interact", response_model=SceneResponse)
async def interact(input: AgentInput):
    """
    Main interaction endpoint for the RPG system
    """
    try: 
        # Build comprehensive game context
        game_context = create_game_context(input)
        
        logger.info(f"Processing interaction for session {input.session_id}")
        logger.info(f"Player choice: {input.player_choice}")
        logger.info(f"Player scenes completed: {input.game_progress.scenes_completed}")
        print(f"Processing interaction for session {input.session_id}")
        print(f"Player choice: {input.player_choice}")
        print(f"Player scenes completed: {input.game_progress.scenes_completed}")  # Fixed
        
        # Get response from coordinated game agents
        raw_result_str = await process_game_turn(game_context, input.session_id) # process_game_turn now expects AgentInput and returns str
        
        # Parse the JSON string result
        result_dict = parse_json_block(raw_result_str)
        
        # Validate and fix the response
        result_dict = validate_and_fix_response(result_dict)
        
        with open('debug_output.json', 'w') as f:
            json.dump(result_dict, f, indent=2)
        
        # Create scene response Pydantic model
        scene_response = SceneResponse(**result_dict)
       
        # Prepare memory data
        memory_data = create_memory_data(input, scene_response)
        
        # Add memory using the service function
        memory_success = add_game_memory(memory, input.session_id, memory_data)
        
        if memory_success:
            logger.info(f"Successfully added memory for session {input.session_id}")
        else:
            logger.warning(f"Failed to add memory for session {input.session_id}")
        
        logger.info(f"Successfully processed interaction for session {input.session_id}")
        return scene_response
        
    except ValueError as e:
        logger.error(f"JSON parsing error for session {input.session_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Response parsing error: {str(e)}")
        
    except Exception as e:
        logger.error(f"Unexpected error for session {input.session_id}: {e}", exc_info=True)
        
        # Return a safe fallback response
        fallback_response_dict = create_fallback_response(input)
        return SceneResponse(**fallback_response_dict)


@router.post("/init")
async def init_game(request: Request):
    """
    Initialize or load a game session
    """
    body = await request.json()
    session_id = body.get("session_id")
    action = body.get("action")
    world = body.get("world", "default")

    
    if action == "new":
        # Clear memories using service function
        clear_success = clear_user_memories(memory, session_id)
       
        if clear_success:
            print(f"world: {world}")
            return {"status": "cleared", "world": world, "message": "New game started."}
        else:
            logger.error(f"Failed to clear previous game data for session {session_id}")
            return {"status": "error", "message": "Failed to clear previous game data."}
    
    elif action == "load":
        # Check if user has memories
        if not get_user_memories(memory, session_id):
            return {"status": "no_memory", "message": "No saved game found."}
        
        # Get user memories using service function
        user_memories = get_user_memories(memory, session_id)
        
        if user_memories:
            # Get the latest memory for scene state
            # Assuming user_memories is ordered by last_updated descending
            latest_memory_record = user_memories[0] 
            latest_memory_data = json.loads(latest_memory_record.to_dict()['memory'])
           
            return {
                "status": "loaded",
                "message": "Game loaded from memory.",
                "memory_summary": [{"memory": m.memory, "last_updated": str(m.last_updated)} for m in user_memories],
                "scene_state": latest_memory_data.get('world'), # This might need to be more specific to what frontend expects
                "latest_memory_data": latest_memory_data # Return the full latest memory data
            }
        else:
            return {"status": "no_memory", "message": "No saved game found."}
    
    else:
        raise HTTPException(status_code=400, detail="Invalid action. Use 'new' or 'load'.")


@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "agents": "ready"}


@router.get("/memory/{session_id}")
async def get_session_memory(session_id: str):
    """
    Get memory summary for a specific session
    """
    try:
        if not get_user_memories(memory, session_id):
            return {"status": "no_memory", "message": "No memories found for this session."}
        
        memory_summary = get_memory_summary(memory, session_id)[0]
        user_memories = get_user_memories(memory, session_id)
        
        return {
            "status": "success",
            "session_id": session_id,
            "memory_count": len(user_memories),
            "memory_summary": memory_summary,
            "memories": [{"memory": m.memory, "last_updated": str(m.last_updated)} for m in user_memories]
        }
        
    except Exception as e:
        logger.error(f"Error retrieving memory for session {session_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to retrieve memory.")


@router.delete("/memory/{session_id}")
async def clear_session_memory(session_id: str):
    """
    Clear all memories for a specific session
    """
    try:
        clear_success = clear_user_memories(memory, session_id)
        
        if clear_success:
            return {"status": "success", "message": f"Cleared all memories for session {session_id}"}
        else:
            logger.error(f"Failed to clear memories for session {session_id}")
            raise HTTPException(status_code=500, detail="Failed to clear memories.")
            
    except Exception as e:
        logger.error(f"Error clearing memory for session {session_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to clear memory.")


def create_fallback_response(input: AgentInput) -> dict:
    """
    Create a fallback response when the main processing fails.
    Returns a dictionary that can be used to construct a SceneResponse Pydantic model.
    """
    default_world_info = WorldInfo(
        name=input.current_world or "Unknown World",
        theme="Uncertainty",
        description="A world shrouded in error.",
        key_locations=[],
        dominant_factions=[],
        major_threats=[],
        cultural_notes=[],
        historical_timeline=[]
    )

    default_location_details = {
        "exits": [],
        "hidden_areas": [],
        "resource_nodes": [],
        "safety_level": 5
    }

    fallback_scene_response_dict = {
        "scene_tag": f"fallback_{input.session_id}",
        "location": input.current_location or "unknown",
        "world": input.current_world or "unknown",
        "narration_text": f"Something unexpected happens as you {input.player_choice.lower()}. The world around you shifts slightly, and you sense new possibilities emerging. An error occurred.",
        "dialogue": [],
        "characters": [],
        "options": ["Look around carefully", "Take a moment to think", "Continue forward"],
        "game_state": GameState(
            relationships={},
            revealed_secrets=[],
            completed_objectives=[],
            failed_objectives=[],
            active_objectives=[],
            location_flags={},
            story_flags={},
            reputation={},
            major_events=[],
            environmental_conditions=EnvironmentalConditions(),
            resource_availability=ResourceAvailability()
        ).model_dump(),
        "inventory_changes": InventoryChanges(
            added_items=[],
            removed_items=[],
            modified_items=[]
        ).model_dump(),
        "current_inventory": [item.model_dump() for item in input.current_inventory],
        "mood_atmosphere": "uncertain",
        "history_entry": "An unexpected error occurred, leading to a fallback scene.",
        "relationship_changes": {},
        "new_secrets": [],
        "new_objectives": [],
        "completed_objectives_this_scene": [],
        "interactive_elements": [],
        "environmental_discoveries": [],
        "threat_updates": [],
        "ambient_events": [],
        "discovered_lore": [],
        "world_info": default_world_info.model_dump(),
        "location_details": default_location_details
    }
    
    # Validate and fix the fallback response to ensure it conforms to the schema
    return validate_and_fix_response(fallback_scene_response_dict)