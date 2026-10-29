'use client';

import { useEffect, useState } from "react";
import { usePlayerSession } from "@/hooks/usePlayerSession";
import { useGameContext } from "@/components/GameContext"; // adjust path as needed


export function useGameMemory(scene: SceneResponse | null) {
  const session_id = usePlayerSession();
  const { gameData, setGameData } = useGameContext();

  const [gameMemory, setGameMemory] = useState<GameMemory | null>(null);
  const [initialized, setInitialized] = useState(false);

  // The server owns saves. Browser storage is only an offline fallback.
  useEffect(() => {
    if (!session_id || initialized) return;
    if (gameData?.worldName && !gameData?.loaded) {
      setGameMemory(null); setInitialized(true); return;
    }
    let cancelled = false;
    const restore = async () => {
      let snapshot: GameMemory | null = null;
      try {
        const res = await fetch("/api/init", {method: "POST", headers: {"Content-Type": "application/json"}, body: JSON.stringify({session_id, action: "load"})});
        if (!res.ok) throw new Error("Save service unavailable");
        const data = await res.json();
        if (data.status === "loaded") snapshot = data.latest_memory_data;
        else localStorage.removeItem("loadedMemory");
      } catch {
        try {
          const local = JSON.parse(localStorage.getItem("loadedMemory") || "null");
          if (local?.session_id === session_id) snapshot = local;
        } catch { localStorage.removeItem("loadedMemory"); }
      }
      if (!cancelled) { setGameMemory(snapshot); setInitialized(true); }
    };
    restore();
    return () => { cancelled = true; };
  }, [initialized, gameData, session_id]);

  // Helper function to create default memory structure (only called when needed)
  const createDefaultMemory = (): GameMemory => {
    const defaultWorldInfo: WorldInfo = {
      name: gameData?.worldName || "default",
      theme: "survival",
      description: "A harsh world where survival is paramount.",
      key_locations: [],
      dominant_factions: [],
      major_threats: [],
      cultural_notes: [],
      historical_timeline: [],
    };

    const defaultGameState: GameState = {
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
    };

    const defaultCurrentScene: CurrentScene = {
      narration_text: "", 
      dialogue: [], 
      characters: [], 
      options: [],
      mood_atmosphere: "neutral", 
      relationship_changes: {}, 
      new_secrets: [],
      interactive_elements: [], 
      environmental_discoveries: [], 
      threat_updates: [],
      ambient_events: [], 
      discovered_lore: [], 
      world_info: defaultWorldInfo,
      location_details: { 
        exits: [], 
        hidden_areas: [], 
        resource_nodes: [], 
        safety_level: 5 
      },
    };

    return {
      session_id,
      last_updated: new Date().toISOString(),
      scene_tag: "game_start",
      location: "",
      world: gameData?.worldName || "default",
      inventory: [],
      game_state: defaultGameState,
      history: [],
      current_scene: defaultCurrentScene,
      play_time_minutes: 0,
      scenes_completed: 0,
      discovered_locations: [], 
      met_characters: [], 
      unlocked_features: [],
      major_story_beats: [], 
      active_side_quests: [], 
      player_choices_history: [],
      world_knowledge: {}, 
      faction_standings: {}, 
      discovered_secrets: [],
      triggered_events: [], 
      player_preferences: {}, 
      resume_context: {},
      lore_collection: [], 
      world_info: defaultWorldInfo
    };
  };

  // Function to initialize memory when starting a new game
  const initializeNewGameMemory = () => {
    const newMemory = createDefaultMemory();
    setGameMemory(newMemory);
    setGameData({ ...gameData, loaded: newMemory });
    localStorage.setItem("loadedMemory", JSON.stringify(newMemory));
    return newMemory;
  };

  // Update gameMemory based on new scenes and save to localStorage
  useEffect(() => {
    if (!scene || !initialized) return;

    setGameMemory(prevMemory => {
      // If we don't have memory yet, create it now (for new games)
      if (!prevMemory) {
        prevMemory = createDefaultMemory();
      }

      if (prevMemory.scene_tag === scene.scene_tag) return prevMemory;
      const newMemory: GameMemory = {
        ...prevMemory,
        session_id,
        last_updated: new Date().toISOString(),
        scene_tag: scene.scene_tag,
        location: scene.location,
        world: scene.world,
        inventory: scene.current_inventory,
        game_state: scene.game_state,
        history: [...(prevMemory.history || []), scene.history_entry].filter(Boolean).slice(-20),
        current_scene: {
          narration_text: scene.narration_text,
          dialogue: scene.dialogue,
          characters: scene.characters,
          options: scene.options,
          mood_atmosphere: scene.mood_atmosphere,
          relationship_changes: scene.relationship_changes,
          new_secrets: scene.new_secrets,
          interactive_elements: scene.interactive_elements,
          environmental_discoveries: scene.environmental_discoveries,
          threat_updates: scene.threat_updates,
          ambient_events: scene.ambient_events,
          discovered_lore: scene.discovered_lore,
          world_info: scene.world_info,
          location_details: scene.location_details
        },
        play_time_minutes: Number(scene.game_state.story_flags.play_time_minutes ?? prevMemory.play_time_minutes),
        scenes_completed: Number(scene.game_state.story_flags.turn ?? prevMemory.scenes_completed),
        discovered_locations: Array.from(new Set([...(prevMemory.discovered_locations || []), scene.location].filter(Boolean))),
        met_characters: Array.from(new Set([...(prevMemory.met_characters || []), ...(scene.characters || []).map(c => c.id)].filter(Boolean))),
        lore_collection: Array.from(new Set([...(prevMemory.lore_collection || []), ...(scene.discovered_lore || [])].map(lore => JSON.stringify(lore)))).map(str => JSON.parse(str)),
        world_info: scene.world_info || prevMemory.world_info,
      };

      // Save updated memory to localStorage immediately
      try {
        localStorage.setItem("loadedMemory", JSON.stringify(newMemory));
        console.log("Game memory saved to localStorage");
      } catch (error) {
        console.error("Failed to save memory to localStorage:", error);
      }

      return newMemory;
    });
  }, [scene, initialized, session_id]);

  // Save memory to localStorage whenever gameMemory changes (additional safety)
  useEffect(() => {
    if (gameMemory && initialized) {
      try {
        localStorage.setItem("loadedMemory", JSON.stringify(gameMemory));
      } catch (error) {
        console.error("Failed to save memory to localStorage:", error);
      }
    }
  }, [gameMemory, initialized]);

  return { gameMemory, initialized, initializeNewGameMemory, replaceMemory: (snapshot: GameMemory) => setGameMemory(snapshot) };
}