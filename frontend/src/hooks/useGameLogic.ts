'use client';

import { useEffect, useState, useRef } from "react";
import { useSession } from "next-auth/react";
import { useGameContext } from '@/components/GameContext';
import { useGameMemory } from "@/hooks/useGameMemory";

export const useGameLogic = () => {
  const { data: session } = useSession();
  const session_id = session?.user?.email || "guest_session";
  const { gameData, setGameData } = useGameContext();

  const [scene, setScene] = useState<SceneResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [gameProgress, setGameProgress] = useState<GameProgressContext>({
    scenes_completed: 0,
    play_time_minutes: 0,
    story_escalation_level: 1,
    tension_level: 1,
    major_story_beats: [],
    active_themes: [],
    world_knowledge: {},
    faction_standings: {},
    player_preferences: {},
    preferred_interaction_types: []
  });

  // Initialize game memory based on context or loaded data
  const { gameMemory, initialized } = useGameMemory(scene);
  
  const [sessionStartTime, setSessionStartTime] = useState(Date.now());
  const hasLoadedInitialScene = useRef(false);

  // Create default structures to prevent backend errors
  const createDefaultWorldInfo = (): WorldInfo => ({
    name: gameMemory?.world || gameData?.worldName || "Unknown World",
    theme: "adventure",
    description: "A mysterious world awaits exploration",
    key_locations: [],
    dominant_factions: [],
    major_threats: [],
    cultural_notes: [],
    historical_timeline: []
  });

  const createDefaultLocationDetails = (): LocationDetails => ({
    exits: [],
    hidden_areas: [],
    resource_nodes: [],
    safety_level: 5
  });

  const createDefaultCurrentScene = (): CurrentSceneContext => ({
    scene_tag: gameMemory?.scene_tag || "start",
    location: gameMemory?.location || "starting_area",
    world: gameMemory?.world || gameData?.worldName || "default_world",
    narration_text: "You find yourself in a new situation...",
    dialogue: [],
    characters: [],
    narrative_options: [],
    interactive_elements: [],
    environmental_discoveries: [],
    mood_atmosphere: "neutral",
    threat_updates: [],
    ambient_events: [],
    relationship_changes: {},
    new_secrets: [],
    new_objectives: [],
    completed_objectives_this_scene: [],
    discovered_lore: [],
    world_info: createDefaultWorldInfo(),
    location_details: createDefaultLocationDetails()
  });

  const createDefaultGameState = (): GameState => ({
    relationships: {},
    revealed_secrets: [],
    completed_objectives: [],
    failed_objectives: [],
    active_objectives: [],
    location_flags: {},
    story_flags: {},
    reputation: {},
    major_events: [],
    environmental_conditions: {
      weather: "clear",
      visibility: "normal",
      temperature: "comfortable",
      hazard_level: 0
    },
    resource_availability: {
      food: "moderate",
      water: "moderate",
      medical_supplies: "scarce",
      shelter_materials: "moderate",
      fuel: "scarce",
      tools: "moderate"
    }
  });

  const createDefaultInventoryChanges = (): InventoryChanges => ({
    added_items: [],
    removed_items: [],
    modified_items: []
  });

  // Helper function to convert GameMemory to SceneResponse for initial load
  const convertGameMemoryToSceneResponse = (gameMemory: GameMemory): SceneResponse => ({
    scene_tag: gameMemory.scene_tag,
    location: gameMemory.location,
    world: gameMemory.world,
    narration_text: gameMemory.current_scene?.narration_text || "You find yourself in a familiar place...",
    dialogue: safeGetArray(gameMemory.current_scene?.dialogue),
    characters: safeGetArray(gameMemory.current_scene?.characters),
    options: safeGetArray(gameMemory.current_scene?.options),
    game_state: safeGetObject(gameMemory.game_state, createDefaultGameState()),
    inventory_changes: createDefaultInventoryChanges(),
    current_inventory: safeGetArray(gameMemory.inventory),
    mood_atmosphere: gameMemory.current_scene?.mood_atmosphere || "neutral",
    history_entry: gameMemory.history?.[gameMemory.history.length - 1] || "",
    relationship_changes: safeGetObject(gameMemory.current_scene?.relationship_changes, {}),
    new_secrets: safeGetArray(gameMemory.current_scene?.new_secrets),
    new_objectives: safeGetArray(gameMemory.game_state?.active_objectives),
    completed_objectives_this_scene: safeGetArray(gameMemory.game_state?.completed_objectives),
    interactive_elements: safeGetArray(gameMemory.current_scene?.interactive_elements),
    environmental_discoveries: safeGetArray(gameMemory.current_scene?.environmental_discoveries),
    threat_updates: safeGetArray(gameMemory.current_scene?.threat_updates),
    ambient_events: safeGetArray(gameMemory.current_scene?.ambient_events),
    discovered_lore: safeGetArray(gameMemory.current_scene?.discovered_lore),
    world_info: safeGetObject(gameMemory.current_scene?.world_info, createDefaultWorldInfo()),
    location_details: safeGetObject(gameMemory.current_scene?.location_details, createDefaultLocationDetails()),
  });

  // Helper function to convert CurrentScene to CurrentSceneContext
  const convertCurrentSceneToContext = (currentScene: CurrentScene, gameMemory: GameMemory): CurrentSceneContext => ({
    scene_tag: gameMemory?.scene_tag || "start",
    location: gameMemory?.location || "starting_area", 
    world: gameMemory?.world || gameData?.worldName || "default_world",
    narration_text: currentScene.narration_text || "You find yourself in a new situation...",
    dialogue: safeGetArray(currentScene.dialogue),
    characters: safeGetArray(currentScene.characters),
    narrative_options: safeGetArray(currentScene.options),
    interactive_elements: safeGetArray(currentScene.interactive_elements),
    environmental_discoveries: safeGetArray(currentScene.environmental_discoveries),
    mood_atmosphere: currentScene.mood_atmosphere || "neutral",
    threat_updates: safeGetArray(currentScene.threat_updates),
    ambient_events: safeGetArray(currentScene.ambient_events),
    relationship_changes: safeGetObject(currentScene.relationship_changes, {}),
    new_secrets: safeGetArray(currentScene.new_secrets),
    new_objectives: safeGetArray(gameMemory?.game_state?.active_objectives),
    completed_objectives_this_scene: safeGetArray(gameMemory?.game_state?.completed_objectives),
    discovered_lore: safeGetArray(currentScene.discovered_lore),
    world_info: safeGetObject(currentScene.world_info, createDefaultWorldInfo()),
    location_details: safeGetObject(currentScene.location_details, createDefaultLocationDetails())
  });

  // Helper function to safely get array property
  const safeGetArray = <T>(arr: T[] | undefined): T[] => arr || [];

  // Helper function to safely get object property
  const safeGetObject = <T>(obj: T | undefined, defaultValue: T): T => obj || defaultValue;

  // Effect for initial game load - handles both loaded games and new games
useEffect(() => {
  if (hasLoadedInitialScene.current) return;

  // Wait for memory initialization to complete
  if (!initialized) return;

  // Case 1: We have loaded game data from memory (either localStorage or context)
  if (gameMemory && initialized) {
    try {
      console.log("Loading existing game from memory...");
      
      // Convert GameMemory to SceneResponse and set scene
      const reconstructedScene = convertGameMemoryToSceneResponse(gameMemory);
      setScene(reconstructedScene);

      // Update game progress with safe property access
      setGameProgress({
        scenes_completed: gameMemory.scenes_completed || 0,
        play_time_minutes: gameMemory.play_time_minutes || 0,
        story_escalation_level: gameMemory.game_state?.story_flags?.story_escalation_level || 1,
        tension_level: gameMemory.game_state?.story_flags?.tension_level || 1,
        major_story_beats: safeGetArray(gameMemory.major_story_beats),
        active_themes: safeGetArray(gameMemory.game_state?.story_flags?.active_themes),
        world_knowledge: safeGetObject(gameMemory.world_knowledge, {}),
        faction_standings: safeGetObject(gameMemory.faction_standings, {}),
        player_preferences: safeGetObject(gameMemory.player_preferences, {}),
        preferred_interaction_types: safeGetArray(gameMemory.player_preferences?.preferred_interaction_types)
      });

      hasLoadedInitialScene.current = true;
      return; // Important: return early to prevent new game creation
    } catch (err) {
      console.error("Error loading game from memory:", err);
      setError("Failed to load game state");
    }
  }

  // Case 2: We have a worldName for a new game (only if no existing memory)
  if (gameData?.worldName && !gameMemory) {
    console.log("Starting new game with world:", gameData.worldName);
    handleChoice(`Start Game in ${gameData.worldName}`, 'narrative_choice');
    hasLoadedInitialScene.current = true;
    return;
  }

  // Case 3: Fallback for completely new games without context or memory
  if (!gameMemory && !gameData?.worldName) {
    console.log("Starting default new game...");
    handleChoice("Start Game", 'narrative_choice');
    hasLoadedInitialScene.current = true;
  }
}, [initialized, gameMemory, gameData?.worldName]); // Updated dependencies

  const handleChoice = async (
    choiceText: string,
    interactionType: UserInteraction['interaction_type'],
    elementId?: string,
    elementType?: string,
    choiceIndex?: number
  ) => {
    if (loading) return;

    setLoading(true);
    setError(null);

    try {
      const currentTime = Date.now();
      const minutesPlayedThisTurn = Math.floor((currentTime - sessionStartTime) / 60000);
      setSessionStartTime(currentTime);

      const updatedPlayTime = gameProgress.play_time_minutes + minutesPlayedThisTurn;
      const updatedScenesCompleted = gameProgress.scenes_completed + 1;

      const updatedGameProgress: GameProgressContext = {
        ...gameProgress,
        scenes_completed: updatedScenesCompleted,
        play_time_minutes: updatedPlayTime,
      };

      // Create safe defaults for required fields - improved for new games
      const currentSceneContext: CurrentSceneContext = gameMemory?.current_scene ? 
        convertCurrentSceneToContext(gameMemory.current_scene, gameMemory) : 
        createDefaultCurrentScene();
      const currentGameState: GameState = gameMemory?.game_state || createDefaultGameState();
      const currentInventory: Item[] = gameMemory?.inventory || [];

      const userInteraction: UserInteraction = {
        interaction_type: interactionType,
        choice_text: choiceText,
        choice_index: choiceIndex,
        element_id: elementId,
        element_type: elementType,
        interaction_context: {
          timestamp: new Date().toISOString(),
          scene_context: scene?.scene_tag || gameMemory?.scene_tag || "start",
          location_context: scene?.location || gameMemory?.location || "starting_area",
          characters_present: safeGetArray(scene?.characters || currentSceneContext.characters).map(c => c.id),
          available_items: safeGetArray(scene?.current_inventory || currentInventory).map(i => i.name),
          active_threats: safeGetArray(scene?.threat_updates || currentSceneContext.threat_updates).filter(t => t.immediate_danger),
          mood_when_chosen: scene?.mood_atmosphere || currentSceneContext.mood_atmosphere || "neutral",
          tension_level: gameProgress.tension_level
        }
      };

      // Build the complete request body with all required fields
      const requestBody: AgentInput = {
        session_id,
        scenes_completed: updatedScenesCompleted,
        user_interaction: userInteraction,
        player_choice: choiceText,
        current_location: gameMemory?.location || "starting_area",
        current_world: gameMemory?.world || gameData?.worldName || "default_world",
        scene_tag: gameMemory?.scene_tag || "start",
        present_characters: safeGetArray(currentSceneContext.characters).map(c => c.id),
        current_scene: currentSceneContext,
        current_inventory: currentInventory,
        game_state: currentGameState,
        game_progress: updatedGameProgress,
        recent_history: safeGetArray(gameMemory?.history),
        agent_hints: {
          player_seems_to_prefer: safeGetObject(gameMemory?.player_preferences, {}),
          story_pacing_hint: updatedScenesCompleted > 50 ? "escalate_toward_climax" : "build_tension",
          interaction_pattern: interactionType,
          last_major_choice: gameMemory?.player_choices_history?.slice(-1)[0] || null,
          world_theme: gameMemory?.world_info?.theme || "survival",
          player_resource_status: currentGameState.resource_availability || { food: "unknown", water: "unknown" }
        },
        emergency_flags: {
          low_health: false,
          high_threat: safeGetArray(currentSceneContext.threat_updates).some(t => t.immediate_danger && t.escalation_level > 7),
          story_climax_approaching: updatedScenesCompleted > 80,
          player_stuck: false,
          critical_resources_low: currentGameState.resource_availability?.food === "critical" || currentGameState.resource_availability?.water === "critical"
        }
      };

      console.log("Sending request to backend:", JSON.stringify(requestBody, null, 2));
      
      const response = await fetch("/api/interact", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(requestBody)
      });

      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(`HTTP error! status: ${response.status}, message: ${errorText}`);
      }

      const data: SceneResponse = await response.json();
      
      // Validate response data
      if (!data.scene_tag || !data.location || !data.world) {
        throw new Error("Invalid response: missing required fields");
      }

      setScene(data);
      
      // Update game progress with safe property access
      setGameProgress(prevProgress => ({
        ...prevProgress,
        scenes_completed: updatedScenesCompleted,
        play_time_minutes: updatedPlayTime,
        story_escalation_level: data.game_state?.story_flags?.story_escalation_level || prevProgress.story_escalation_level,
        tension_level: data.game_state?.story_flags?.tension_level || prevProgress.tension_level,
        major_story_beats: safeGetArray(data.game_state?.major_events),
        active_themes: safeGetArray(data.game_state?.story_flags?.active_themes),
        world_knowledge: safeGetObject(data.game_state?.story_flags?.world_knowledge, prevProgress.world_knowledge),
        faction_standings: safeGetObject(data.game_state?.reputation, prevProgress.faction_standings),
        player_preferences: safeGetObject(data.game_state?.story_flags?.player_preferences, prevProgress.player_preferences),
        preferred_interaction_types: safeGetArray(data.game_state?.story_flags?.preferred_interaction_types)
      }));

      // Update gameData context after successful interaction
      setGameData({ 
        ...gameData,
        loaded: data 
      });

    } catch (err) {
      console.error("Error fetching scene:", err);
      const errorMessage = err instanceof Error ? err.message : "An unexpected error occurred";
      setError(`Failed to process choice: ${errorMessage}`);
    } finally {
      setLoading(false);
    }
  };

  // Sync frontend memory with error handling
  useEffect(() => {
    if (!gameMemory) return;

    const syncFrontendMemory = () => {
      try {
        setGameData({ 
          ...gameData,
          loaded: gameMemory 
        });
        console.log("Frontend memory synced.");
      } catch (err) {
        console.error("Failed to sync frontend memory:", err);
        setError("Failed to sync game state");
      }
    };

    const handler = setTimeout(syncFrontendMemory, 1000);
    return () => clearTimeout(handler);
  }, [gameMemory, gameProgress]);

  // Reset error when scene changes
  useEffect(() => {
    if (scene) {
      setError(null);
    }
  }, [scene]);

  return { 
    scene, 
    loading, 
    error, 
    gameProgress, 
    initialized, 
    handleChoice,
    // Additional utility functions
    resetError: () => setError(null)
  };
};