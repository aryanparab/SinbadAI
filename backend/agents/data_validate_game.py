def validate_and_fix_response(result_dict):
    """
    Comprehensive validation and fixing function that ensures all fields 
    from the SceneResponse Pydantic model are present with correct defaults.
    
    This function goes through ALL fields from the schema and verifies each one,
    adding default values for any missing required fields.
    """
    import json
    from datetime import datetime
    
    # =====================================================
    # HELPER FUNCTIONS
    # =====================================================
    
    def validate_string_length(text, min_len, max_len, field_name):
        """Ensure string length is within bounds"""
        if not text or len(text) < min_len:
            return f"Default {field_name} content to meet minimum length requirement."
        if len(text) > max_len:
            return text[:max_len-3] + "..."
        return text
    
    def validate_numeric_range(value, min_val, max_val, default_val):
        """Ensure numeric value is within range"""
        if not isinstance(value, (int, float)):
            return default_val
        return max(min_val, min(max_val, value))
    
    def ensure_list(value, default_factory=list):
        """Ensure value is a list, default to empty list"""
        if value is None:
            return default_factory()
        if not isinstance(value, list):
            return default_factory()
        return value
    
    def ensure_dict(value, default_factory=dict):
        """Ensure value is a dict, default to empty dict"""
        if value is None:
            return default_factory()
        if not isinstance(value, dict):
            return default_factory()
        return value
    
    # =====================================================
    # SCENE RESPONSE TOP-LEVEL FIELDS VALIDATION
    # =====================================================
    
    # 1. scene_tag: str
    if not result_dict.get('scene_tag'):
        result_dict['scene_tag'] = f"scene_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        print(f"⚠️ Added default scene_tag: {result_dict['scene_tag']}")
    
    # 2. location: str
    if not result_dict.get('location'):
        result_dict['location'] = "Unknown Location"
        print(f"⚠️ Added default location")
    
    # 3. world: str
    if not result_dict.get('world'):
        result_dict['world'] = "Unknown World"
        print(f"⚠️ Added default world")
    
    # 4. narration_text: str (200-2000 chars)
    if 'narration_text' in result_dict:
        result_dict['narration_text'] = validate_string_length(
            result_dict['narration_text'], 200, 2000, 'narration'
        )
    else:
        result_dict['narration_text'] = "You find yourself in an unfamiliar place, uncertain of what comes next."
        print(f"⚠️ Added default narration_text")
    
    # 5. dialogue: List[DialogueLine]
    if 'dialogue' not in result_dict or not isinstance(result_dict['dialogue'], list):
        result_dict['dialogue'] = []
        print(f"⚠️ Added default dialogue: []")
    
    # 6. characters: List[Character]
    if 'characters' not in result_dict or not isinstance(result_dict['characters'], list):
        result_dict['characters'] = []
        print(f"⚠️ Added default characters: []")
    else:
        # Validate each character
        for char in result_dict['characters']:
            if not isinstance(char, dict):
                char = {}
                result_dict['characters'][result_dict['characters'].index(char if isinstance(char, dict) else {})] = char
            
            # Validate numeric ranges
            char['relationship_level'] = validate_numeric_range(
                char.get('relationship_level', 0), -10, 10, 0
            )
            char['trust_level'] = validate_numeric_range(
                char.get('trust_level', 0), -10, 10, 0
            )
            
            # Required character fields
            required_char_fields = {
                'id': 'unknown',
                'name': 'Unknown',
                'avatar': 'default_avatar.png',
                'interactable': True,
                'current_mood': 'neutral',
                'memories': [],
                'personal_objectives': [],
                'knowledge_flags': {}
            }
            for field, default in required_char_fields.items():
                if field not in char:
                    char[field] = default
                    print(f"⚠️ Added default {field} to character")
            
            # Optional character fields - set to null if empty
            optional_char_fields = ['backstory', 'faction', 'skills', 'equipment']
            for field in optional_char_fields:
                if field in char and (char[field] == "" or char[field] == []):
                    char[field] = None
    
    # 7. options: List[str] (2-6 items)
    if 'options' not in result_dict or not isinstance(result_dict['options'], list):
        result_dict['options'] = ["Continue", "Look around"]
        print(f"⚠️ Added default options")
    else:
        # Ensure options is a list of strings
        result_dict['options'] = [str(opt) for opt in result_dict['options']]
        if len(result_dict['options']) < 2:
            result_dict['options'].extend(["Continue", "Look around"][:2-len(result_dict['options'])])
        elif len(result_dict['options']) > 6:
            result_dict['options'] = result_dict['options'][:6]
        print(f"⚠️ Fixed options count: {len(result_dict['options'])}")
    
    # =====================================================
    # 8. game_state: GameState (COMPLETE VALIDATION)
    # =====================================================
    
    # Ensure game_state exists
    if 'game_state' not in result_dict or not isinstance(result_dict['game_state'], dict):
        result_dict['game_state'] = {}
        print(f"⚠️ Created empty game_state dict")
    
    gs = result_dict['game_state']
    
    # GameState field mappings: field_name -> (type, default)
    game_state_field_defaults = {
        # Dict[str, int]
        'relationships': (dict, {}),
        # List[str]
        'revealed_secrets': (list, []),
        'completed_objectives': (list, []),
        'failed_objectives': (list, []),
        'major_events': (list, []),
        # Dict[str, bool]
        'location_flags': (dict, {}),
        # Dict[str, Any]
        'story_flags': (dict, {}),
        # Dict[str, str]
        'reputation': (dict, {}),
    }
    
    for field, (field_type, default) in game_state_field_defaults.items():
        if field not in gs:
            gs[field] = default
            print(f"⚠️ Added default game_state.{field}")
        elif not isinstance(gs[field], field_type):
            gs[field] = default
            print(f"⚠️ Fixed game_state.{field} type")
    
    # Handle field name mappings (AI sometimes uses wrong field names)
    # player_reputation -> reputation
    if 'player_reputation' in gs and 'reputation' not in gs:
        gs['reputation'] = gs['player_reputation']
        del gs['player_reputation']
        print(f"⚠️ Mapped player_reputation -> reputation")
    
    # major_story_events -> major_events
    if 'major_story_events' in gs and 'major_events' not in gs:
        gs['major_events'] = gs['major_story_events']
        del gs['major_story_events']
        print(f"⚠️ Mapped major_story_events -> major_events")
    
    # GameState nested: environmental_conditions
    if 'environmental_conditions' not in gs or not isinstance(gs['environmental_conditions'], dict):
        gs['environmental_conditions'] = {
            "weather": "clear",
            "visibility": "normal",
            "temperature": "comfortable",
            "hazard_level": 0
        }
        print(f"⚠️ Added default game_state.environmental_conditions")
    else:
        ec = gs['environmental_conditions']
        ec_defaults = {
            "weather": "clear",
            "visibility": "normal",
            "temperature": "comfortable",
        }
        for field, default in ec_defaults.items():
            if field not in ec:
                ec[field] = default
        ec['hazard_level'] = validate_numeric_range(ec.get('hazard_level', 0), 0, 10, 0)
    
    # GameState nested: resource_availability
    if 'resource_availability' not in gs or not isinstance(gs['resource_availability'], dict):
        gs['resource_availability'] = {
            "food": "moderate",
            "water": "moderate",
            "medical_supplies": "scarce",
            "shelter_materials": "moderate",
            "fuel": "scarce",
            "tools": "moderate"
        }
        print(f"⚠️ Added default game_state.resource_availability")
    else:
        ra = gs['resource_availability']
        ra_defaults = {
            "food": "moderate",
            "water": "moderate",
            "medical_supplies": "scarce",
            "shelter_materials": "moderate",
            "fuel": "scarce",
            "tools": "moderate"
        }
        for field, default in ra_defaults.items():
            if field not in ra:
                ra[field] = default
                print(f"⚠️ Added default game_state.resource_availability.{field}")
    
    # GameState nested: active_objectives
    if 'active_objectives' not in gs or not isinstance(gs['active_objectives'], list):
        gs['active_objectives'] = []
        print(f"⚠️ Added default game_state.active_objectives: []")
    else:
        for obj in gs['active_objectives']:
            if not isinstance(obj, dict):
                obj = {}
                continue
            
            obj['progress'] = validate_numeric_range(obj.get('progress', 0), 0, 100, 0)
            obj['escalation_level'] = validate_numeric_range(obj.get('escalation_level', 1), 1, 10, 1)
            
            # Required objective fields
            if 'id' not in obj:
                obj['id'] = f"obj_{datetime.now().strftime('%H%M%S')}"
            if 'description' not in obj:
                obj['description'] = "Complete this objective"
            if 'quest_type' not in obj:
                obj['quest_type'] = "main"
            if 'completed' not in obj:
                obj['completed'] = False
            if 'involves_npcs' not in obj:
                obj['involves_npcs'] = []
            
            # Optional objective fields
            if 'rewards' in obj and (not isinstance(obj['rewards'], list) or obj['rewards'] == []):
                obj['rewards'] = None
            if obj.get('time_limit') in ["", "None"]:
                obj['time_limit'] = None
    
    # =====================================================
    # 9. inventory_changes: InventoryChanges
    # =====================================================
    
    if 'inventory_changes' not in result_dict or not isinstance(result_dict['inventory_changes'], dict):
        result_dict['inventory_changes'] = {
            "added_items": [],
            "removed_items": [],
            "modified_items": []
        }
        print(f"⚠️ Added default inventory_changes")
    else:
        ic = result_dict['inventory_changes']
        for field in ['added_items', 'removed_items', 'modified_items']:
            if field not in ic or not isinstance(ic[field], list):
                ic[field] = []
    
    # =====================================================
    # 10. current_inventory: List[Item]
    # =====================================================
    
    if 'current_inventory' not in result_dict or not isinstance(result_dict['current_inventory'], list):
        result_dict['current_inventory'] = []
        print(f"⚠️ Added default current_inventory: []")
    else:
        fixed_inventory = []
        for item in result_dict['current_inventory']:
            if isinstance(item, str):
                fixed_inventory.append({
                    "name": item,
                    "quantity": 1,
                    "description": f"A mysterious item named {item}.",
                    "durability": 100,
                    "item_type": "misc",
                    "properties": {}
                })
            elif isinstance(item, dict):
                item.setdefault("name", "unknown_item")
                item.setdefault("quantity", 1)
                item.setdefault("description", f"No description for {item.get('name', 'unknown')}")
                item["durability"] = validate_numeric_range(item.get("durability", 100), 0, 100, 100)
                item.setdefault("item_type", "misc")
                item.setdefault("properties", {})
                fixed_inventory.append(item)
        result_dict['current_inventory'] = fixed_inventory
    
    # =====================================================
    # 11. mood_atmosphere: str
    # =====================================================
    
    if not result_dict.get('mood_atmosphere'):
        result_dict['mood_atmosphere'] = 'neutral'
        print(f"⚠️ Added default mood_atmosphere: neutral")
    
    # =====================================================
    # 12. history_entry: str (50-500 chars)
    # =====================================================
    
    if 'history_entry' in result_dict:
        result_dict['history_entry'] = validate_string_length(
            result_dict['history_entry'], 50, 500, 'history entry'
        )
    else:
        result_dict['history_entry'] = "A new scene begins, the story continuing its journey."
        print(f"⚠️ Added default history_entry")
    
    # =====================================================
    # 13. relationship_changes: Dict[str, int]
    # =====================================================
    
    if 'relationship_changes' not in result_dict or not isinstance(result_dict['relationship_changes'], dict):
        result_dict['relationship_changes'] = {}
        print(f"⚠️ Added default relationship_changes: {{}}")
    else:
        fixed_changes = {}
        for char_id, change_value in result_dict['relationship_changes'].items():
            if isinstance(change_value, dict):
                if 'relationship_level' in change_value:
                    fixed_changes[char_id] = validate_numeric_range(
                        change_value['relationship_level'], -10, 10, 0
                    )
                else:
                    fixed_changes[char_id] = 0
            elif isinstance(change_value, (int, float)):
                fixed_changes[char_id] = validate_numeric_range(
                    change_value, -10, 10, 0
                )
            else:
                fixed_changes[char_id] = 0
        result_dict['relationship_changes'] = fixed_changes
    
    # =====================================================
    # 14. new_secrets: List[str]
    # =====================================================
    
    if 'new_secrets' not in result_dict or not isinstance(result_dict['new_secrets'], list):
        result_dict['new_secrets'] = []
        print(f"⚠️ Added default new_secrets: []")
    
    # =====================================================
    # 15. new_objectives: List[QuestObjective]
    # =====================================================
    
    if 'new_objectives' not in result_dict or not isinstance(result_dict['new_objectives'], list):
        result_dict['new_objectives'] = []
        print(f"⚠️ Added default new_objectives: []")
    else:
        for obj in result_dict['new_objectives']:
            if not isinstance(obj, dict):
                obj = {}
                continue
            obj['progress'] = validate_numeric_range(obj.get('progress', 0), 0, 100, 0)
            obj['escalation_level'] = validate_numeric_range(obj.get('escalation_level', 1), 1, 10, 1)
            if 'id' not in obj:
                obj['id'] = f"obj_{datetime.now().strftime('%H%M%S')}"
            if 'description' not in obj:
                obj['description'] = "Complete this objective"
            if 'quest_type' not in obj:
                obj['quest_type'] = "main"
            if 'completed' not in obj:
                obj['completed'] = False
            if 'involves_npcs' not in obj:
                obj['involves_npcs'] = []
            if 'rewards' in obj and (not isinstance(obj['rewards'], list) or obj['rewards'] == []):
                obj['rewards'] = None
            if obj.get('time_limit') in ["", "None"]:
                obj['time_limit'] = None
    
    # =====================================================
    # 16. completed_objectives_this_scene: List[str]
    # =====================================================
    
    if 'completed_objectives_this_scene' not in result_dict or not isinstance(result_dict['completed_objectives_this_scene'], list):
        result_dict['completed_objectives_this_scene'] = []
        print(f"⚠️ Added default completed_objectives_this_scene: []")
    
    # =====================================================
    # 17. interactive_elements: List[InteractiveElement]
    # =====================================================
    
    if 'interactive_elements' not in result_dict or not isinstance(result_dict['interactive_elements'], list):
        result_dict['interactive_elements'] = []
        print(f"⚠️ Added default interactive_elements: []")
    else:
        for elem in result_dict['interactive_elements']:
            if not isinstance(elem, dict):
                elem = {}
                continue
            if elem.get('side_quest_trigger') in [{}, "", None]:
                elem['side_quest_trigger'] = None
    
    # =====================================================
    # 18. environmental_discoveries: List[EnvironmentalDiscovery]
    # =====================================================
    
    if 'environmental_discoveries' not in result_dict or not isinstance(result_dict['environmental_discoveries'], list):
        result_dict['environmental_discoveries'] = []
        print(f"⚠️ Added default environmental_discoveries: []")
    
    # =====================================================
    # 19. threat_updates: List[ThreatUpdate]
    # =====================================================
    
    if 'threat_updates' not in result_dict or not isinstance(result_dict['threat_updates'], list):
        result_dict['threat_updates'] = []
        print(f"⚠️ Added default threat_updates: []")
    else:
        for threat in result_dict['threat_updates']:
            if not isinstance(threat, dict):
                threat = {}
                continue
            threat['escalation_level'] = validate_numeric_range(
                threat.get('escalation_level', 1), 1, 10, 1
            )
    
    # =====================================================
    # 20. ambient_events: List[AmbientEvent]
    # =====================================================
    
    if 'ambient_events' not in result_dict or not isinstance(result_dict['ambient_events'], list):
        result_dict['ambient_events'] = []
        print(f"⚠️ Added default ambient_events: []")
    
    # =====================================================
    # 21. discovered_lore: List[LoreEntry]
    # =====================================================
    
    if 'discovered_lore' not in result_dict or not isinstance(result_dict['discovered_lore'], list):
        result_dict['discovered_lore'] = []
        print(f"⚠️ Added default discovered_lore: []")
    else:
        valid_categories = ['history', 'character', 'location', 'faction', 'event', 'artifact']
        for lore in result_dict['discovered_lore']:
            if not isinstance(lore, dict):
                lore = {}
                continue
            if 'category' not in lore or lore['category'] not in valid_categories:
                lore['category'] = 'history'
            if 'discovered_at' not in lore or not lore['discovered_at']:
                lore['discovered_at'] = datetime.now().isoformat() + 'Z'
            lore['importance_level'] = validate_numeric_range(
                lore.get('importance_level', 1), 1, 10, 1
            )
    
    # =====================================================
    # 22. world_info: WorldInfo (CRITICAL - MUST BE OBJECT, NOT STRING)
    # =====================================================
    
    if 'world_info' not in result_dict:
        # Create default WorldInfo object
        result_dict['world_info'] = {
            "name": "Unknown World",
            "theme": "Adventure",
            "description": "A world of mystery and adventure.",
            "key_locations": [],
            "dominant_factions": [],
            "major_threats": [],
            "cultural_notes": [],
            "historical_timeline": []
        }
        print(f"⚠️ Added default world_info")
    elif isinstance(result_dict['world_info'], str):
        # Handle string values like "default_world_info" - convert to object
        result_dict['world_info'] = {
            "name": result_dict['world_info'],
            "theme": "Adventure",
            "description": "A world of mystery and adventure.",
            "key_locations": [],
            "dominant_factions": [],
            "major_threats": [],
            "cultural_notes": [],
            "historical_timeline": []
        }
        print(f"⚠️ Converted string world_info to object")
    elif isinstance(result_dict['world_info'], dict):
        wi = result_dict['world_info']
        # Fix historical_timeline if it's a dict
        if 'historical_timeline' in wi and isinstance(wi['historical_timeline'], dict):
            wi['historical_timeline'] = [wi['historical_timeline']]
        # Ensure all required WorldInfo fields exist
        world_info_defaults = {
            "name": "Unknown World",
            "theme": "Adventure",
            "description": "A world of mystery and adventure.",
            "key_locations": [],
            "dominant_factions": [],
            "major_threats": [],
            "cultural_notes": [],
            "historical_timeline": []
        }
        for field, default in world_info_defaults.items():
            if field not in wi:
                wi[field] = default
                print(f"⚠️ Added default world_info.{field}")
    
    # =====================================================
    # 23. location_details: LocationDetails (CRITICAL - MUST BE OBJECT, NOT STRING)
    # =====================================================
    
    if 'location_details' not in result_dict:
        # Create default LocationDetails object
        result_dict['location_details'] = {
            "exits": [],
            "hidden_areas": [],
            "resource_nodes": [],
            "safety_level": 5
        }
        print(f"⚠️ Added default location_details")
    elif isinstance(result_dict['location_details'], str):
        # Handle string values like "default_location_details" - convert to object
        result_dict['location_details'] = {
            "exits": [],
            "hidden_areas": [],
            "resource_nodes": [],
            "safety_level": 5
        }
        print(f"⚠️ Converted string location_details to object")
    elif isinstance(result_dict['location_details'], dict):
        ld = result_dict['location_details']
        ld['safety_level'] = validate_numeric_range(ld.get('safety_level', 5), 1, 10, 5)
        # Ensure all required LocationDetails fields exist
        location_details_defaults = {
            "exits": [],
            "hidden_areas": [],
            "resource_nodes": []
        }
        for field, default in location_details_defaults.items():
            if field not in ld:
                ld[field] = default
                print(f"⚠️ Added default location_details.{field}")
    
    # =====================================================
    # FINAL VALIDATION: Validate game_state relationships
    # =====================================================
    
    if 'game_state' in result_dict and isinstance(result_dict['game_state'], dict):
        gs = result_dict['game_state']
        if 'relationships' in gs and isinstance(gs['relationships'], dict):
            fixed_relationships = {}
            for char_id, val in gs['relationships'].items():
                try:
                    fixed_val = int(val)
                except (ValueError, TypeError):
                    if isinstance(val, str) and "/" in val:
                        try:
                            fixed_val = int(val.split("/")[0].strip())
                        except:
                            fixed_val = 0
                    else:
                        fixed_val = 0
                fixed_val = max(-10, min(10, fixed_val))
                fixed_relationships[char_id] = fixed_val
            gs['relationships'] = fixed_relationships
    
    # =====================================================
    # FINAL DEBUG OUTPUT
    # =====================================================
    
    print(f"\n{'='*50}")
    print(f"FINAL VALIDATED RESPONSE:")
    print(f"  scene_tag: {result_dict.get('scene_tag', 'MISSING')}")
    print(f"  location: {result_dict.get('location', 'MISSING')}")
    print(f"  world: {result_dict.get('world', 'MISSING')}")
    print(f"  narration_text: {len(result_dict.get('narration_text', ''))} chars")
    print(f"  history_entry: {len(result_dict.get('history_entry', ''))} chars")
    print(f"  mood_atmosphere: {result_dict.get('mood_atmosphere', 'MISSING')}")
    
    # Game state validation status
    gs = result_dict.get('game_state', {})
    print(f"  game_state.relationships: {len(gs.get('relationships', {}))} entries")
    print(f"  game_state.failed_objectives: {len(gs.get('failed_objectives', []))} entries")
    print(f"  game_state.location_flags: {len(gs.get('location_flags', {}))} entries")
    print(f"  game_state.reputation: {len(gs.get('reputation', {}))} entries")
    print(f"  game_state.major_events: {len(gs.get('major_events', []))} entries")
    print(f"  game_state.resource_availability.shelter_materials: {gs.get('resource_availability', {}).get('shelter_materials', 'MISSING')}")
    print(f"  world_info type: {type(result_dict.get('world_info')).__name__}")
    print(f"  location_details type: {type(result_dict.get('location_details')).__name__}")
    print(f"{'='*50}\n")

    return result_dict

# Additional helper function for parsing JSON blocks
import re

def fix_json_common_errors(json_str: str) -> str:
    """
    Attempts to fix common issues in JSON output from Gemma-based models:
    - Unescaped internal double quotes
    - Wrong contractions like he"s
    - Smart quotes and invalid unicode
    - Trailing commas
    """
    # Replace smart quotes with plain quotes
    json_str = json_str.replace("'", "'").replace("'", "'").replace(""", '"').replace(""", '"').replace("'", "'").replace("'", "'")

    # Fix common contraction issues (e.g., He"s → He's)
    json_str = re.sub(r'\b(\w+)"s\b', r"\1's", json_str)

    # Escape unescaped quotes inside long text fields
    def escape_quotes_inside_strings(match):
        key = match.group(1)
        value = match.group(2)
        # Escape quotes inside the value
        fixed_value = value.replace('\\"', '"')  # unescape safe escapes first
        fixed_value = fixed_value.replace('"', '\\"')
        return f'"{key}": "{fixed_value}"'

    # Apply to likely text fields
    json_str = re.sub(r'"(narration_text|history_entry|backstory|content|description|text)"\s*:\s*"([^"]*?)"', escape_quotes_inside_strings, json_str)

    # Remove trailing commas in objects and arrays
    json_str = re.sub(r',\s*([\]}])', r'\1', json_str)

    # Remove newline control characters
    json_str = json_str.replace("\r", "").replace("\n", "\\n")

    return json_str

def parse_json_block(raw_result_str):
    import json
    import re

    json_pattern = r'```json\s*(\{.*?\})\s*```'
    match = re.search(json_pattern, raw_result_str, re.DOTALL)

    if match:
        json_str = match.group(1)
    else:
        json_pattern = r'(\{.*\})'
        match = re.search(json_pattern, raw_result_str, re.DOTALL)
        if not match:
            raise ValueError("No JSON found in response")
        json_str = match.group(1)

    try:
        return json.loads(json_str)
    except json.JSONDecodeError:
        json_str = fix_json_common_errors(json_str)
        try:
            return json.loads(json_str)
        except json.JSONDecodeError as e:
            snippet = json_str[:500]
            raise ValueError(f"Invalid JSON format: {e}\nProblematic snippet: {snippet}")

