// types.ts
// Core item and inventory models
interface Item {
  name: string;
  quantity: number;
  description: string;
  durability: number; // 0-100
  item_type: string;
  properties: Record<string, any>;
}

interface InventoryChange {
  name: string;
  quantity: number;
  reason?: string;
  durability_change?: number;
  new_properties?: Record<string, any>;
}

interface InventoryChanges {
  added_items: Item[];
  removed_items: Item[];
  modified_items: Item[];
}

// Character and dialogue models
interface DialogueLine {
  speaker: string;
  text: string;
  emotion: string;
  is_internal_thought: boolean;
  audible_to: string[];
}

interface Character {
  id: string;
  name: string;
  avatar: string;
  interactable: boolean;
  relationship_level: number; // -10 to 10
  current_mood: string;
  trust_level: number; // -10 to 10
  memories: string[];
  personal_objectives: string[];
  knowledge_flags: Record<string, boolean>;
  backstory?: string;
  faction?: string;
  skills?: string[];
  equipment?: string[];
}

// Quest and objective models
interface QuestObjective {
  id: string;
  description: string;
  quest_type: string;
  completed: boolean;
  involves_npcs: string[];
  progress: number; // 0-100
  escalation_level: number; // 1-10
  rewards?: string[];
  time_limit?: string;
}

// Environmental models
interface EnvironmentalConditions {
  weather: string;
  visibility: string;
  temperature: string;
  hazard_level: number; // 0-10
}

interface ResourceAvailability {
  food: string;
  water: string;
  medical_supplies: string;
  shelter_materials: string;
  fuel: string;
  tools: string;
}

// Core game state
interface GameState {
  relationships: Record<string, number>;
  revealed_secrets: string[];
  completed_objectives: string[];
  failed_objectives: string[];
  active_objectives: QuestObjective[];
  location_flags: Record<string, boolean>;
  story_flags: Record<string, any>;
  reputation: Record<string, string>;
  major_events: string[];
  environmental_conditions: EnvironmentalConditions;
  resource_availability: ResourceAvailability;
}

// Interactive elements and discoveries
interface InteractiveElement {
  id: string;
  name: string;
  description: string;
  interaction_types: string[];
  requires_items: string[];
  unlocks_options: string[];
  options: string[];
  potential_outcomes: Record<string, string>;
  side_quest_trigger?: Record<string, any>;
}

interface EnvironmentalDiscovery {
  name: string;
  description: string;
  significance: string;
  unlocks_content: string[];
}

interface ThreatUpdate {
  threat_id: string;
  threat_name: string;
  escalation_level: number; // 1-10
  immediate_danger: boolean;
  resolution_methods: string[];
  affects_npcs: string[];
}

interface AmbientEvent {
  event_type: string;
  description: string;
  affects_mood: boolean;
  creates_opportunities: string[];
}

// Lore and World Building
interface LoreEntry {
  id: string;
  title: string;
  content: string;
  category: 'history' | 'character' | 'location' | 'faction' | 'event' | 'artifact';
  discovered_at: string;
  related_entries: string[];
  importance_level: number; // 1-10
}

interface WorldInfo {
  name: string;
  theme: string;
  description: string;
  key_locations: string[];
  dominant_factions: string[];
  major_threats: string[];
  cultural_notes: string[];
  historical_timeline: Array<{
    period: string;
    events: string[];
  }>;
}

// Enhanced input models
interface UserInteraction {
  interaction_type: 'narrative_choice' | 'character_interaction' | 'item_interaction' | 'location_interaction' | 'quest_interaction' | 'environmental_interaction';
  choice_text: string;
  choice_index?: number;
  element_id?: string;
  element_type?: string;
  interaction_context: Record<string, any>;
}

interface LocationDetails {
  exits: string[];
  hidden_areas: string[];
  resource_nodes: string[];
  safety_level: number; // 1-10
}

interface CurrentSceneContext {
  scene_tag: string;
  location: string;
  world: string;
  narration_text: string;
  dialogue: DialogueLine[];
  characters: Character[];
  narrative_options: string[];
  interactive_elements: InteractiveElement[];
  environmental_discoveries: EnvironmentalDiscovery[];
  mood_atmosphere: string;
  threat_updates: ThreatUpdate[];
  ambient_events: AmbientEvent[];
  relationship_changes: Record<string, number>;
  new_secrets: string[];
  new_objectives: QuestObjective[];
  completed_objectives_this_scene: string[];
  discovered_lore: LoreEntry[];
  world_info: WorldInfo;
  location_details: LocationDetails;
}

interface GameProgressContext {
  scenes_completed: number;
  play_time_minutes: number;
  story_escalation_level: number; // 1-10
  tension_level: number; // 1-10
  major_story_beats: string[];
  active_themes: string[];
  world_knowledge: Record<string, any>;
  faction_standings: Record<string, string>;
  player_preferences: Record<string, any>;
  preferred_interaction_types: string[];
}

// Enhanced agent input
interface AgentInput {
  session_id: string;
  scenes_completed: number;
  user_interaction: UserInteraction;
  player_choice: string; // Legacy field for backward compatibility
  current_location: string;
  current_world: string;
  scene_tag?: string;
  present_characters: string[];
  current_scene: CurrentSceneContext;
  current_inventory: Item[];
  game_state: GameState;
  game_progress: GameProgressContext;
  recent_history: string[];
  agent_hints: Record<string, any>;
  emergency_flags: Record<string, boolean>;
}

// Enhanced scene response
interface SceneResponse {
  scene_tag: string;
  location: string;
  world: string;
  narration_text: string; // 200-2000 characters
  dialogue: DialogueLine[];
  characters: Character[];
  options: string[]; // 2-6 options
  game_state: GameState;
  inventory_changes: InventoryChanges;
  current_inventory: Item[];
  mood_atmosphere: string;
  history_entry: string; // 50-500 characters
  relationship_changes: Record<string, number>;
  new_secrets: string[];
  new_objectives: QuestObjective[];
  completed_objectives_this_scene: string[];
  interactive_elements: InteractiveElement[];
  environmental_discoveries: EnvironmentalDiscovery[];
  threat_updates: ThreatUpdate[];
  ambient_events: AmbientEvent[];
  discovered_lore: LoreEntry[];
  world_info: WorldInfo;
  location_details: LocationDetails;
}

// Enhanced memory model
interface CurrentScene {
  narration_text: string;
  dialogue: DialogueLine[];
  characters: Character[];
  options: string[];
  mood_atmosphere: string;
  relationship_changes: Record<string, number>;
  new_secrets: string[];
  interactive_elements: InteractiveElement[];
  environmental_discoveries: EnvironmentalDiscovery[];
  threat_updates: ThreatUpdate[];
  ambient_events: AmbientEvent[];
  discovered_lore: LoreEntry[];
  world_info: WorldInfo;
  location_details: LocationDetails;
}

interface GameMemory {
  session_id: string;
  last_updated: string; // ISO datetime string
  scene_tag: string;
  location: string;
  world: string;
  inventory: Item[];
  game_state: GameState;
  history: string[];
  current_scene: CurrentScene;
  play_time_minutes: number;
  scenes_completed: number;
  discovered_locations: string[];
  met_characters: string[];
  unlocked_features: string[];
  major_story_beats: string[];
  active_side_quests: string[];
  player_choices_history: Array<Record<string, any>>;
  world_knowledge: Record<string, any>;
  faction_standings: Record<string, string>;
  discovered_secrets: string[];
  triggered_events: string[];
  player_preferences: Record<string, any>;
  resume_context: Record<string, any>;
  lore_collection: LoreEntry[];
  world_info: WorldInfo;
}