I'm building a procedural narrative game with a thrilling story, dynamic world generation, and multi-dimensional choices. The stack is:

- **React** frontend (with clickable NPCs, items, quests, locations)
- **FastAPI (Python)** backend
- **Agno** for multi-agent orchestration
- Agents built as tools communicating with a central **orchestrator agent**
- Responses follow a strict **SceneResponse JSON format**, validated against Pydantic and TypeScript interfaces

---

## 🎮 Game Vision

- Players begin by entering a **theme prompt** (e.g., "Jurassic Park", "Zombie Apocalypse", "Deserted Island")
- The world, characters, threats, and story **evolve procedurally** based on player choices
- The game world introduces new **NPCs**, **locations**, **items**, **emergent quests**, **side stories**, and **escalating threats**
- The story is designed to be **tense and climactic** — ending within ~100–150 moves
- Players can **branch** the narrative by clicking on NPCs, new items, or side stories (e.g., exploring a mysterious hole becomes a new main quest)

---

## 🧱 Game Architecture

- Each user action is routed to the **orchestrator agent**
- The orchestrator gathers partial outputs from multiple **specialist agents**
- Final output is a full **SceneResponse JSON**
- Each scene contains:
  - narration_text
  - characters: [Character]
  - dialogue: [DialogueLine]
  - options: [string]
  - game_state: GameState (relationships, objectives, flags, secrets)
  - inventory_changes
  - history_entry
  - mood_atmosphere
  - relationship_changes
  - new_objectives / secrets / completed_objectives_this_scene

---

## 🧠 Multi-Agent System (Agno)

The orchestrator agent calls **12 specialist agents**, each contributing only their part.

---

### 🔁 Agent Prompt Pattern Example

```python
threat_tool = Agent(
  name="threat_agent",
  model=groq_model,
  instructions="""
  You are the tension architect, responsible for creating and managing dynamic threats.
  Only focus on threats (monsters, ghosts, disasters, stalkers, etc).
  Provide:
  - Specific threat descriptions
  - Escalation triggers
  - NPC responses
  - Resolution methods
  Don't output full JSON.
  """
)
📦 Agent Descriptions
narrative_agent – The Atmosphere Weaver
Writes immersive, sensory-rich narration_text

Blends world, mood, threat, and NPC elements

Uses internal thoughts, pacing, foreshadowing

npc_agent – The Character Architect
Creates new NPCs with:

Emotional states

Relationships

Personal objectives

Dialogue hooks

Suggests interactions (e.g., help, question, accuse)

Updates memories and trust levels

worldbuilder_agent – The Environment Designer
Adds environmental details:

Biomes (jungles, ruins, caves)

Structures (labs, shelters, bunkers)

Local lore, weather, decay, ambient effects

Updates location_flags and story_flags

threat_agent – The Tension Engineer
Injects danger into the scene:

Physical threats: monsters, storms, radiation

Social threats: betrayal, suspicion

Escalation paths: threat grows if ignored

Updates major_events, mood_atmosphere, NPC behavior

quest_agent – The Storyline Strategist
Adds new active_objectives

Tracks main vs side quests

Updates progress, completed, failed objectives

Transforms world features (e.g. “hole” → new main quest)

emotion_agent – The Sentiment Synthesizer
Adjusts:

current_mood of NPCs

relationship_level and trust_level

Dialogue tone (anger, hope, desperation)

Affects branching dialogue outcomes

event_agent – The Random Encounter Curator
Creates ambient, spontaneous moments:

Arguments between NPCs

Lost children crying

Hidden notes, booby traps

Often generates optional interaction branches

item_agent – The Inventory Engineer
Introduces new items (e.g., medkits, encrypted radios)

Items can unlock options or serve as scene tools

Adds inventory_changes, supports crafting/upgrades

structure_agent – The World Builder
Adds interactive buildings or structures:

Condition: e.g. locked, broken, guarded

Options: enter, repair, search

Risk/Reward: hideout vs trap

Modifies location_flags, generates optional exploration paths

lore_agent – The Canon Keeper
Maintains narrative consistency:

Validates new NPCs, threats, items against world history

Aligns story_flags, secrets, reputation

Prevents contradictions in long-play sessions

choice_agent – The Option Designer
Suggests 3–5 actionable options for the player

Based on: inventory, NPCs, mood, current objective

Ensures meaningful consequences for each option

dialogue_agent – The Conversational Director
Creates multi-speaker dialogue lines

Includes:

Emotion per line

audible_to list

Internal thoughts vs spoken words

Anchors character relationships via speech

⚙️ Dynamic Interaction Logic (Frontend + Backend)
Clicking an NPC shows multiple interactions (help, accuse, ask for past)

Discovering a hole, shelter, or signal tower spawns interaction options

Any interactable can initiate a new scene or quest

Dynamic subplots (e.g., “Help Elara find her lost brother”) are initiated by NPCs

“Side story” can become “Main quest” if player chooses to follow it

Use present_characters, story_flags, and major_events to track dynamic forks


🧠 Orchestrator Agent Instructions
The orchestrator_agent must:

Route player input to all agents

Combine partial outputs into a final SceneResponse JSON

Ensure:

All fields present

Proper data types

Valid JSON

Maintain pacing, emotional arc, and interactivity