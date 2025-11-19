# pydantic_models.py
from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any, Literal
from datetime import datetime

# Core item and inventory models
class Item(BaseModel):
    name: str
    quantity: int
    description: str
    durability: int = Field(ge=0, le=100)  # 0-100
    item_type: str
    properties: Dict[str, Any]

class InventoryChange(BaseModel):
    name: str
    quantity: int
    reason: Optional[str] = None
    durability_change: Optional[int] = None
    new_properties: Optional[Dict[str, Any]] = None

class InventoryChanges(BaseModel):
    added_items: List[Item]
    removed_items: List[Item]
    modified_items: List[Item]

# Character and dialogue models
class DialogueLine(BaseModel):
    speaker: str
    text: str
    emotion: str
    is_internal_thought: bool
    audible_to: List[str]

class Character(BaseModel):
    id: str
    name: str
    avatar: str
    interactable: bool
    relationship_level: int = Field(ge=-10, le=10)  # -10 to 10
    current_mood: str
    trust_level: int = Field(ge=-10, le=10)  # -10 to 10
    memories: List[str]
    personal_objectives: List[str]
    knowledge_flags: Dict[str, Any]
    backstory: Optional[str] = None
    faction: Optional[str] = None
    skills: Optional[List[str]] = None
    equipment: Optional[List[str]] = None

# Quest and objective models
class QuestObjective(BaseModel):
    id: str
    description: str
    quest_type: str
    completed: bool
    involves_npcs: List[str]
    progress: int = Field(ge=0, le=100)  # 0-100
    escalation_level: int = Field(ge=1, le=10)  # 1-10
    rewards: Optional[List[str]] = None
    time_limit: Optional[str] = None

# Environmental models
class EnvironmentalConditions(BaseModel):
    weather: str
    visibility: str
    temperature: str
    hazard_level: int = Field(ge=0, le=10)  # 0-10

class ResourceAvailability(BaseModel):
    food: str
    water: str
    medical_supplies: str
    shelter_materials: str
    fuel: str
    tools: str

# Core game state
class GameState(BaseModel):
    """Core persistent game state"""
    relationships: Dict[str, int]
    revealed_secrets: List[str]
    completed_objectives: List[str]
    failed_objectives: List[str]
    active_objectives: List[QuestObjective]
    location_flags: Dict[str, bool]
    story_flags: Dict[str, Any]
    reputation: Dict[str, str]
    major_events: List[str]
    environmental_conditions: EnvironmentalConditions
    resource_availability: ResourceAvailability

class InteractiveElement(BaseModel):
    id: str
    name: str
    description: str
    interaction_types: List[str]
    requires_items: List[str]
    unlocks_options: List[str]
    options: List[str]
    potential_outcomes: Dict[str, str]
    side_quest_trigger: Optional[Dict[str, Any]] = None

class EnvironmentalDiscovery(BaseModel):
    name: str
    description: str
    significance: str
    unlocks_content: List[str]

class ThreatUpdate(BaseModel):
    threat_id: str
    threat_name: str
    escalation_level: int = Field(ge=1, le=10)  # 1-10
    immediate_danger: bool
    resolution_methods: List[str]
    affects_npcs: List[str]

class AmbientEvent(BaseModel):
    event_type: str
    description: str
    affects_mood: bool
    creates_opportunities: List[str]

# Lore and World Building
class LoreEntry(BaseModel):
    id: str
    title: str
    content: str
    category: Literal['history', 'character', 'location', 'faction', 'event', 'artifact']
    discovered_at: str
    related_entries: List[str]
    importance_level: int = Field(ge=1, le=10)  # 1-10

class WorldInfo(BaseModel):
    name: str
    theme: str
    description: str
    key_locations: List[str]
    dominant_factions: List[str]
    major_threats: List[str]
    cultural_notes: List[str]
    historical_timeline: List[Dict[str, List[str]]]

# Enhanced input models
class UserInteraction(BaseModel):
    """Captures the type and details of user interaction"""
    interaction_type: Literal["narrative_choice", "character_interaction", "item_interaction", "location_interaction", "quest_interaction", "environmental_interaction"]
    choice_text: str
    choice_index: Optional[int] = None
    element_id: Optional[str] = None
    element_type: Optional[str] = None
    interaction_context: Dict[str, Any]

class LocationDetails(BaseModel):
    exits: List[str]
    hidden_areas: List[str]
    resource_nodes: List[str]
    safety_level: int = Field(ge=1, le=10)  # 1-10

class CurrentSceneContext(BaseModel):
    """Complete context of the current scene"""
    scene_tag: str
    location: str
    world: str
    narration_text: str
    dialogue: List[DialogueLine]
    characters: List[Character]
    narrative_options: List[str]
    interactive_elements: List[InteractiveElement]
    environmental_discoveries: List[EnvironmentalDiscovery]
    mood_atmosphere: str
    threat_updates: List[ThreatUpdate]
    ambient_events: List[AmbientEvent]
    relationship_changes: Dict[str, int]
    new_secrets: List[str]
    new_objectives: List[QuestObjective]
    completed_objectives_this_scene: List[str]
    discovered_lore: List[LoreEntry]
    world_info: WorldInfo
    location_details: LocationDetails

class GameProgressContext(BaseModel):
    """Context about overall game progression"""
    scenes_completed: int
    play_time_minutes: int
    story_escalation_level: int = Field(ge=1, le=10)  # 1-10
    tension_level: int = Field(ge=1, le=10)  # 1-10
    major_story_beats: List[str]
    active_themes: List[str]
    world_knowledge: Dict[str, Any]
    faction_standings: Dict[str, str]
    player_preferences: Dict[str, Any]
    preferred_interaction_types: List[str]

# Updated AgentInput model
class AgentInput(BaseModel):
    """Enhanced input model for multi-agent orchestration"""
    session_id: str
    scenes_completed: int
    user_interaction: UserInteraction
    player_choice: str  # Legacy field for backward compatibility
    current_location: str
    current_world: str
    scene_tag: Optional[str] = None
    present_characters: List[str]
    current_scene: CurrentSceneContext
    current_inventory: List[Item]
    game_state: GameState
    game_progress: GameProgressContext
    recent_history: List[str]
    agent_hints: Dict[str, Any]
    emergency_flags: Dict[str, bool]
    
    class Config:
        extra = "ignore"
        validate_assignment = True

# Output model - what comes back from AI
class SceneResponse(BaseModel):
    scene_tag: str
    location: str
    world: str
    narration_text: str = Field(max_length=2000)  # 200-2000 characters
    dialogue: List[DialogueLine]
    characters: List[Character]
    options: List[str] = Field( max_items=6)  # 2-6 options
    game_state: GameState
    inventory_changes: InventoryChanges
    current_inventory: List[Item]
    mood_atmosphere: str
    history_entry: str = Field(min_length=50, max_length=500)  # 50-500 characters
    relationship_changes: Dict[str, int]
    new_secrets: List[str]
    new_objectives: List[QuestObjective]
    completed_objectives_this_scene: List[str]
    interactive_elements: List[InteractiveElement]
    environmental_discoveries: List[EnvironmentalDiscovery]
    threat_updates: List[ThreatUpdate]
    ambient_events: List[AmbientEvent]
    discovered_lore: List[LoreEntry]
    world_info: WorldInfo
    location_details: LocationDetails
    
    class Config:
        extra = "ignore"
        validate_assignment = True

# Memory data structure for save/load
class CurrentScene(BaseModel):
    narration_text: str
    dialogue: List[DialogueLine]
    characters: List[Character]
    options: List[str]
    mood_atmosphere: str
    relationship_changes: Dict[str, int]
    new_secrets: List[str]
    interactive_elements: List[InteractiveElement]
    environmental_discoveries: List[EnvironmentalDiscovery]
    threat_updates: List[ThreatUpdate]
    ambient_events: List[AmbientEvent]
    discovered_lore: List[LoreEntry]
    world_info: WorldInfo
    location_details: LocationDetails

class GameMemory(BaseModel):
    """Complete game state for save/load and scene continuity"""
    session_id: str
    last_updated: str  # ISO datetime string
    scene_tag: str
    location: str
    world: str
    inventory: List[Item]
    game_state: GameState
    history: List[str]
    current_scene: CurrentScene
    play_time_minutes: int
    scenes_completed: int
    discovered_locations: List[str]
    met_characters: List[str]
    unlocked_features: List[str]
    major_story_beats: List[str]
    active_side_quests: List[str]
    player_choices_history: List[Dict[str, Any]]
    world_knowledge: Dict[str, Any]
    faction_standings: Dict[str, str]
    discovered_secrets: List[str]
    triggered_events: List[str]
    player_preferences: Dict[str, Any]
    resume_context: Dict[str, Any]
    lore_collection: List[LoreEntry]
    world_info: WorldInfo