'use client';

import { useEffect, useState } from "react";
import { useSession } from "next-auth/react";
import { useGameContext } from "@/components/GameContext"; // adjust path as needed


export function useGameMemory(scene: SceneResponse | null) {
  const { data: session } = useSession();
  const session_id = session?.user?.email || "guest_session";
  const { gameData, setGameData } = useGameContext();

  const [gameMemory, setGameMemory] = useState<GameMemory | null>(null);
  const [initialized, setInitialized] = useState(false);

  // Load memory from localStorage first, then context, then server
  useEffect(() => {
    if (!initialized) {
      // Priority 1: Check localStorage first (for refresh scenarios)
      const local = localStorage.getItem("loadedMemory");
      if (local) {
        try {
          const parsed = JSON.parse(local);
          console.log("Loading game memory from localStorage");
          setGameMemory(parsed);
          setGameData({ ...gameData, loaded: parsed });
          setInitialized(true);
          return;
        } catch (error) {
          console.error("Failed to parse localStorage memory:", error);
          localStorage.removeItem("loadedMemory"); // Clear corrupted data
        }
      }

      // Priority 2: Check context if localStorage is empty
      if (gameData?.loaded) {
        console.log("Loading game memory from context");
        setGameMemory(gameData.loaded);
        // Save to localStorage for future refreshes
        localStorage.setItem("loadedMemory", JSON.stringify(gameData.loaded));
        setInitialized(true);
        return;
      }

      // Priority 3: Try loading from server if nothing in local or context
      const loadFromServer = async () => {
        try {
          console.log("Attempting to load game memory from server");
          const res = await fetch("/api/init", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ session_id, action: "load" }),
          });
          const data = await res.json();
          if (data.status === "loaded") {
            const memory = data.latest_memory_data;
            console.log("Loaded game memory from server");
            setGameMemory(memory);
            setGameData({ ...gameData, loaded: memory });
            localStorage.setItem("loadedMemory", JSON.stringify(memory));
          } else {
            console.log("No existing memory found, will wait for new game to start");
            // DON'T create default memory here - let the game logic handle new games
            setGameMemory(null);
          }
        } catch (error) {
          console.error("Failed to load memory from server:", error);
          // DON'T create default memory here either - let the game logic handle it
          setGameMemory(null);
        }
        setInitialized(true);
      };

      loadFromServer();
    }
  }, [initialized, gameData, session_id, setGameData]);

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
        play_time_minutes: prevMemory.play_time_minutes,
        scenes_completed: prevMemory.scenes_completed + 1, // Increment scenes completed
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

  // Cleanup function to save memory before component unmounts
  useEffect(() => {
    return () => {
      if (gameMemory) {
        try {
          localStorage.setItem("loadedMemory", JSON.stringify(gameMemory));
          console.log("Game memory saved on cleanup");
        } catch (error) {
          console.error("Failed to save memory on cleanup:", error);
        }
      }
    };
  }, [gameMemory]);

  return { gameMemory, initialized, initializeNewGameMemory };
}