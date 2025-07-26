'use client';

import { useEffect, useState } from "react";
import { useSession } from "next-auth/react";
import { useGameContext } from '@/components/GameContext';
import { useGameMemory } from "@/hooks/useGameMemory";

// Updated GameScreen component
export default function GameScreen() {
  const { data: session } = useSession();
  const session_id = session?.user?.email || "guest_session";
  const { gameData } = useGameContext();

  const [scene, setScene] = useState<SceneResponse | null>(null);
  const [loading, setLoading] = useState(false);
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

  // Custom hook handles memory loading + updating
  const { gameMemory, initialized } = useGameMemory(scene);

  // Track player session start time for play time calculation
  const [sessionStartTime] = useState(Date.now());

  // Rehydrate scene from memory when initialized
  useEffect(() => {
    if (initialized && !scene) {
      if (gameMemory) {
        const reconstructedScene: SceneResponse = {
          scene_tag: gameMemory.scene_tag,
          location: gameMemory.location,
          world: gameMemory.world,
          current_inventory: gameMemory.inventory,
          game_state: gameMemory.game_state,
          ...gameMemory.current_scene,
          inventory_changes: { added_items: [], removed_items: [], modified_items: [] },
          history_entry: "",
          new_objectives: [],
          completed_objectives_this_scene: [],
          interactive_elements: gameMemory.current_scene.interactive_elements || [],
          environmental_discoveries: gameMemory.current_scene.environmental_discoveries || [],
          threat_updates: gameMemory.current_scene.threat_updates || [],
          ambient_events: gameMemory.current_scene.ambient_events || []
        };
        setScene(reconstructedScene);
        
        // Restore game progress from memory
        setGameProgress({
          scenes_completed: gameMemory.scenes_completed,
          play_time_minutes: gameMemory.play_time_minutes,
          story_escalation_level: Math.min(Math.floor(gameMemory.scenes_completed / 10) + 1, 10),
          tension_level: Math.min(Math.floor(gameMemory.scenes_completed / 8) + 1, 10),
          major_story_beats: gameMemory.major_story_beats,
          active_themes:  [],
          world_knowledge: gameMemory.world_knowledge,
          faction_standings: gameMemory.faction_standings,
          player_preferences: gameMemory.player_preferences,
          preferred_interaction_types: gameMemory.player_preferences.preferred_interaction_types || []
        });
      } else {
        // No memory found — fallback to start new game
        handleChoice("Start Game", 'narrative_choice');
      }
    }
  }, [initialized, gameMemory, scene]);

  // Enhanced choice handler with interaction context
  const handleChoice = async (
    choiceText: string, 
    interactionType: 'narrative_choice' | 'character_interaction' | 'item_interaction' | 'location_interaction' | 'quest_interaction' | 'environmental_interaction',
    elementId?: string,
    elementType?: string,
    choiceIndex?: number
  ) => {
    if (!session_id) return;
    setLoading(true);

    // Update play time
    const currentPlayTime = Math.floor((Date.now() - sessionStartTime) / 60000);
    const updatedGameProgress = {
      ...gameProgress,
      play_time_minutes: gameProgress.play_time_minutes + currentPlayTime,
      scenes_completed: scene ? gameProgress.scenes_completed + 1 : 0
    };

    // Create comprehensive user interaction context
    const userInteraction: UserInteraction = {
      interaction_type: interactionType,
      choice_text: choiceText,
      choice_index: choiceIndex,
      element_id: elementId,
      element_type: elementType,
      interaction_context: {
        timestamp: new Date().toISOString(),
        scene_context: scene?.scene_tag,
        location_context: scene?.location,
        characters_present: scene?.characters?.map(c => c.id) || [],
        available_items: scene?.current_inventory?.map(i => i.name) || [],
        active_threats: scene?.threat_updates?.filter(t => t.immediate_danger) || [],
        mood_when_chosen: scene?.mood_atmosphere,
        tension_level: updatedGameProgress.tension_level
      }
    };

    // Build comprehensive current scene context
    const currentSceneContext: CurrentSceneContext = scene ? {
      scene_tag: scene.scene_tag,
      location: scene.location,
      world: scene.world,
      narration_text: scene.narration_text,
      dialogue: scene.dialogue,
      characters: scene.characters,
      narrative_options: scene.options,
      interactive_elements: scene.interactive_elements || [],
      environmental_discoveries: scene.environmental_discoveries || [],
      mood_atmosphere: scene.mood_atmosphere,
      threat_updates: scene.threat_updates || [],
      ambient_events: scene.ambient_events || [],
      relationship_changes: scene.relationship_changes || {},
      new_secrets: scene.new_secrets || [],
      new_objectives: scene.new_objectives || [],
      completed_objectives_this_scene: scene.completed_objectives_this_scene || []
    } : {
      scene_tag: "game_start",
      location: "",
      world: gameData?.worldName || "default",
      narration_text: "",
      dialogue: [],
      characters: [],
      narrative_options: [],
      interactive_elements: [],
      environmental_discoveries: [],
      mood_atmosphere: "mysterious",
      threat_updates: [],
      ambient_events: [],
      relationship_changes: {},
      new_secrets: [],
      new_objectives: [],
      completed_objectives_this_scene: []
    };

    // Enhanced agent input with comprehensive context
    const requestBody: AgentInput = {
      session_id,
      scenes_completed:gameProgress.scenes_completed,
      user_interaction: userInteraction,
      player_choice: choiceText, // Legacy compatibility
      current_location: scene?.location || "",
      current_world: scene?.world || gameData?.worldName || "default",
      scene_tag: scene?.scene_tag,
      present_characters: scene?.characters?.map(c => c.id) || [],
      current_scene: currentSceneContext,
      current_inventory: scene?.current_inventory || [
        { name: "flashlight", quantity: 1, description: "A reliable flashlight", durability: 100, item_type: "tool", properties: {} }
      ],
      game_state: scene?.game_state || {
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
          weather: "unknown",
          visibility: "normal",
          temperature: "comfortable",
          hazard_level: 0
        },
        resource_availability: {
          food: "unknown",
          water: "unknown",
          medical_supplies: "unknown",
          shelter_materials: "unknown",
          fuel: "unknown",
          tools: "unknown"
        }
      },
      game_progress: updatedGameProgress,
      recent_history: gameMemory?.history.slice(-10) || [],
      agent_hints: {
        player_seems_to_prefer: gameMemory?.player_preferences || {},
        story_pacing_hint: updatedGameProgress.scenes_completed > 50 ? "escalate_toward_climax" : "build_tension",
        interaction_pattern: interactionType,
        last_major_choice: gameMemory?.player_choices_history?.slice(-1)[0] || null,
        world_theme:  "survival"
      },
      emergency_flags: {
        low_health: false, // Could be determined from game state
        high_threat: scene?.threat_updates?.some(t => t.immediate_danger && t.escalation_level > 7) || false,
        story_climax_approaching: updatedGameProgress.scenes_completed > 80,
        player_stuck: false // Could track if player keeps choosing same options
      }
    };

    try {
      const response = await fetch("/api/interact", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(requestBody)
      });

      const data: SceneResponse = await response.json();
      setScene(data);
      setGameProgress(updatedGameProgress);

    } catch (err) {
      console.error("Error fetching scene:", err);
    }

    setLoading(false);
  };

  // Auto-save memory to backend every time it changes
  useEffect(() => {
    if (!gameMemory) return;

    const saveMemory = async () => {
      try {
        await fetch("/api/save-game", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            ...gameMemory,
            play_time_minutes: gameProgress.play_time_minutes,
            scenes_completed: gameProgress.scenes_completed
          })
        });
        console.log("Auto-saved memory to backend.");
      } catch (err) {
        console.error("Failed to auto-save memory:", err);
      }
    };

    saveMemory();
  }, [gameMemory, gameProgress]);

  // UI rendering part
  if (!initialized) return <div className="p-4">Loading game...</div>;
  
  return (
    <div className="p-6 max-w-4xl mx-auto">
      <div className="mb-6">
        <h1 className="text-3xl font-bold mb-2 text-center">{scene?.world} Survival</h1>
        <div className="flex justify-center space-x-4 text-sm text-gray-600">
          <span>Scenes: {gameProgress.scenes_completed}</span>
          <span>Play Time: {Math.floor(gameProgress.play_time_minutes / 60)}h {gameProgress.play_time_minutes % 60}m</span>
          <span>Tension: {gameProgress.tension_level}/10</span>
        </div>
      </div>

      {loading && <div className="text-center p-4">Loading next scene...</div>}

      {!loading && scene && (
        <div className="space-y-6">
          {/* Main Scene Content */}
          <div className="bg-gray-100 p-6 rounded-lg shadow">
            <h2 className="text-xl font-semibold mb-3">Scene: {scene.scene_tag}</h2>
            <p className="text-gray-800 mb-4 leading-relaxed">{scene.narration_text}</p>
            <div className="flex justify-between text-sm text-gray-500">
              <span>Location: {scene.location}</span>
              <span>Mood: {scene.mood_atmosphere}</span>
            </div>
          </div>

          {/* Dialogue Section */}
          {scene.dialogue && scene.dialogue.length > 0 && (
            <div className="bg-white p-4 rounded-lg shadow">
              <h3 className="font-semibold mb-3">Dialogue:</h3>
              <div className="space-y-2">
                {scene.dialogue.map((line, idx) => (
                  <div key={idx} className="border-l-4 border-blue-300 pl-3">
                    <div className="flex items-center gap-2">
                      <strong className="text-blue-700">{line.speaker}:</strong>
                      {line.emotion && (
                        <span className="text-xs bg-blue-100 px-2 py-1 rounded">{line.emotion}</span>
                      )}
                    </div>
                    <p className="text-gray-700">{line.text}</p>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Characters Section */}
          {scene.characters && scene.characters.length > 0 && (
            <div className="bg-white p-4 rounded-lg shadow">
              <h3 className="font-semibold mb-3">Characters Present:</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {scene.characters.map((char) => (
                  <div
                    key={char.id}
                    className={`p-3 border rounded-lg cursor-pointer transition-colors ${
                      char.interactable ? 'hover:bg-blue-50 border-blue-200' : 'bg-gray-50'
                    }`}
                    onClick={() => char.interactable && handleChoice(`Talk to ${char.name}`, 'character_interaction', char.id, 'npc')}
                  >
                    <h4 className="font-bold text-lg">{char.name}</h4>
                    <div className="text-sm text-gray-600 space-y-1">
                      <p>Relationship: {char.relationship_level > 0 ? '+' : ''}{char.relationship_level}</p>
                      <p>Trust: {char.trust_level > 0 ? '+' : ''}{char.trust_level}</p>
                      <p>Mood: {char.current_mood}</p>
                    </div>
                    {char.interactable && (
                      <div className="mt-2 text-xs text-blue-600">Click to interact</div>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Interactive Elements */}
          {scene.interactive_elements && scene.interactive_elements.length > 0 && (
            <div className="bg-white p-4 rounded-lg shadow">
              <h3 className="font-semibold mb-3">Interactive Elements:</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                {scene.interactive_elements.map((element) => (
                  <div
                    key={element.id}
                    className="p-3 border rounded-lg cursor-pointer hover:bg-green-50 border-green-200"
                  >
                    <h4 className="font-bold">{element.name}</h4>
                    <p className="text-sm text-gray-600 mb-2">{element.description}</p>
                    <div className="flex flex-wrap gap-1">
                      {element.interaction_types.map((type, idx) => (
                        <button
                          key={idx}
                          onClick={() => handleChoice(`${type} ${element.name}`, 'environmental_interaction', element.id, 'interactive_element')}
                          className="text-xs bg-green-100 hover:bg-green-200 px-2 py-1 rounded"
                        >
                          {type}
                        </button>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Inventory Changes */}
          {scene.inventory_changes && 
           (scene.inventory_changes.added_items.length > 0 || 
            scene.inventory_changes.removed_items.length > 0 ||
            scene.inventory_changes.modified_items.length > 0) && (
            <div className="bg-yellow-50 p-4 rounded-lg shadow">
              <h3 className="font-semibold mb-3">Inventory Changes:</h3>
              {scene.inventory_changes.added_items.length > 0 && (
                <div className="mb-2">
                  <p className="text-green-700 font-medium">Added Items:</p>
                  {scene.inventory_changes.added_items.map((item, idx) => (
                    <div key={idx} className="ml-4 text-sm">
                      <span className="font-medium">{item.name}</span> x{item.quantity}
                      {item.description && <span className="text-gray-600"> - {item.description}</span>}
                    </div>
                  ))}
                </div>
              )}
              {scene.inventory_changes.removed_items.length > 0 && (
                <div className="mb-2">
                  <p className="text-red-700 font-medium">Removed Items:</p>
                  {scene.inventory_changes.removed_items.map((item, idx) => (
                    <div key={idx} className="ml-4 text-sm">
                      <span className="font-medium">{item.name}</span> x{item.quantity}
                    </div>
                  ))}
                </div>
              )}
              <div className="mt-3 pt-3 border-t">
                <p className="text-sm text-gray-600">Current Inventory:</p>
                <div className="flex flex-wrap gap-2 mt-1">
                  {scene.current_inventory.map((item, idx) => (
                    <span
                      key={idx}
                      className="text-xs bg-gray-100 px-2 py-1 rounded cursor-pointer hover:bg-gray-200"
                      onClick={() => handleChoice(`Examine ${item.name}`, 'item_interaction', item.name, 'inventory_item')}
                    >
                      {item.name} x{item.quantity}
                    </span>
                  ))}
                </div>
              </div>
            </div>
          )}

          {/* Threats and Events */}
          {scene.threat_updates && scene.threat_updates.length > 0 && (
            <div className="bg-red-50 p-4 rounded-lg shadow">
              <h3 className="font-semibold mb-3 text-red-800">Threat Updates:</h3>
              {scene.threat_updates.map((threat, idx) => (
                <div key={idx} className="mb-3 p-3 bg-white rounded border-l-4 border-red-400">
                  <div className="flex justify-between items-start">
                    <h4 className="font-bold text-red-700">{threat.threat_name}</h4>
                    <span className="text-xs bg-red-100 px-2 py-1 rounded">Level {threat.escalation_level}</span>
                  </div>
                  {threat.immediate_danger && (
                    <p className="text-sm text-red-600 font-medium mt-1">⚠️ Immediate Danger!</p>
                  )}
                  <div className="text-sm text-gray-600 mt-2">
                    Possible solutions: {threat.resolution_methods.join(', ')}
                  </div>
                </div>
              ))}
            </div>
          )}

          {/* Active Objectives */}
          {scene.game_state?.active_objectives?.length > 0 && (
            <div className="bg-blue-50 p-4 rounded-lg shadow">
              <h3 className="font-semibold mb-3 text-blue-800">Active Objectives:</h3>
              <div className="space-y-2">
                {scene.game_state.active_objectives.map((objective, idx) => (
                  <div key={idx} className="bg-white p-3 rounded border-l-4 border-blue-400">
                    <div className="flex justify-between items-start">
                      <h4 className="font-medium">{objective.description}</h4>
                      <span className="text-xs bg-blue-100 px-2 py-1 rounded">{objective.progress}%</span>
                    </div>
                    {objective.involves_npcs.length > 0 && (
                      <p className="text-sm text-gray-600 mt-1">
                        Involves: {objective.involves_npcs.join(', ')}
                      </p>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Main Choice Options */}
          {scene.options && scene.options.length > 0 && (
            <div className="bg-white p-4 rounded-lg shadow">
              <h3 className="font-semibold mb-3">What do you do?</h3>
              <div className="space-y-2">
                {scene.options.map((option, idx) => (
                  <button
                    key={idx}
                    onClick={() => handleChoice(option, 'narrative_choice', undefined, undefined, idx)}
                    className="w-full text-left px-4 py-3 bg-gradient-to-r from-blue-600 to-blue-700 text-white rounded-lg hover:from-blue-700 hover:to-blue-800 transition-all duration-200 shadow-sm"
                  >
                    {option}
                  </button>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}