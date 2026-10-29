"""Three editable director prompts with a shared output contract."""
import json
from pathlib import Path

ROOT = Path(__file__).parent

def build_director_instructions():
    example = {
        "scene_title": "An original title for this scene", "chapter_title": "An original chapter title",
        "scene_tag": "opening", "world": "chosen world", "location": "specific location",
        "narration_text": "Two to four paragraphs, with paragraph breaks.",
        "dialogue": [{"speaker": "A named recurring ally", "text": "A short line revealing the ally’s agenda", "emotion": "restrained", "is_internal_thought": False, "audible_to": ["Sinbad"]}],
        "characters": [{"id": "stable_ally_id", "name": "A named recurring ally", "avatar": "", "interactable": True, "relationship_level": 0, "current_mood": "conflicted", "trust_level": 0, "memories": [], "personal_objectives": ["A specific personal motivation"], "knowledge_flags": {}, "backstory": "A history consistent with the chosen world", "faction": "A faction established in this world"}],
        "options": ["A strategic commitment with a cost", "A genuinely different strategic commitment"],
        "choice_stakes": ["The first approach has this concrete cost", "The second approach has a different concrete cost"],
        "mission": {"id": "opening_mission", "title": "An original mission title", "objective": "A concrete objective tied to the main conflict", "stakes": "Specific stakes grounded in the chosen world", "ally_id": "stable_ally_id"},
        "encounter": {"id": "opening_obstacle", "kind": "rescue", "title": "A specific playable obstacle", "description": "Describe the immediate playable objective in this world", "enemy_name": "A concrete obstacle or opponent", "reward": None, "props": [{"id": "scene_cover", "name": "A world-specific place of cover", "description": "A tangible object already established in the narration", "kind": "cover", "item": None}]},
        "ending_summary": "", "game_state": {"relationships": {}, "active_objectives": [], "story_flags": {}},
        "inventory_changes": {"added_items": [], "removed_items": [], "modified_items": []},
        "current_inventory": [], "history_entry": "A concise record of the decision and its actual consequences, at least fifty characters.",
        "relationship_changes": {}, "new_secrets": [], "new_objectives": [], "completed_objectives_this_scene": [],
        "interactive_elements": [{"id": "scene_object", "name": "An object established in this scene", "description": "Its visible condition and potential use", "options": ["A specific action using this object"], "requires_items": [], "interaction_types": ["use"], "unlocks_options": [], "potential_outcomes": {"use": "A concrete consequence"}}], "discovered_lore": []
    }
    return "\n\n".join((ROOT / name).read_text() for name in ("story.md", "mission.md", "combat.md")) + "\n\nReturn ONLY a valid JSON object. The example illustrates the SHAPE, not this campaign's story. Use the user's world and plan. Populate these fields; unused lists are empty. On the opening include story_plan as instructed. Empty game_state fields are preserved by server rules.\n" + json.dumps(example)
