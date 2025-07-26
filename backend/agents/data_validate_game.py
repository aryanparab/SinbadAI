def validate_and_fix_response(result_dict):
    """Enhanced validation and fixing function"""
    import json
    from datetime import datetime
    
    # Helper function to ensure string length
    def validate_string_length(text, min_len, max_len, field_name):
        if not text or len(text) < min_len:
            return f"Default {field_name} content to meet minimum length requirement."
        if len(text) > max_len:
            return text[:max_len-3] + "..."
        return text
    
    # Helper function to ensure numeric ranges
    def validate_numeric_range(value, min_val, max_val, default_val):
        if not isinstance(value, (int, float)):
            return default_val
        return max(min_val, min(max_val, value))
    
    # Fix narration_text length
    if 'narration_text' in result_dict:
        result_dict['narration_text'] = validate_string_length(
            result_dict['narration_text'], 200, 2000, 'narration'
        )
    
    # Fix history_entry length
    if 'history_entry' in result_dict:
        result_dict['history_entry'] = validate_string_length(
            result_dict['history_entry'], 50, 500, 'history entry'
        )
    
    # Fix options count
    if 'options' in result_dict:
        if not isinstance(result_dict['options'], list):
            result_dict['options'] = ["Continue", "Look around"]
        elif len(result_dict['options']) < 2:
            result_dict['options'].extend(["Continue", "Look around"][:2-len(result_dict['options'])])
        elif len(result_dict['options']) > 6:
            result_dict['options'] = result_dict['options'][:6]
    
    # Fix characters array
    if 'characters' in result_dict:
        for char in result_dict['characters']:
            # Validate numeric ranges
            char['relationship_level'] = validate_numeric_range(
                char.get('relationship_level', 0), -10, 10, 0
            )
            char['trust_level'] = validate_numeric_range(
                char.get('trust_level', 0), -10, 10, 0
            )
            
            # Ensure required fields exist
            required_fields = ['id', 'name', 'avatar', 'interactable', 'current_mood', 'memories', 'personal_objectives', 'knowledge_flags']
            for field in required_fields:
                if field not in char:
                    if field in ['memories', 'personal_objectives']:
                        char[field] = []
                    elif field == 'knowledge_flags':
                        char[field] = {}
                    elif field == 'interactable':
                        char[field] = True
                    else:
                        char[field] = f"default_{field}"
            if not isinstance(char.get("avatar"), str) or not char["avatar"]:
                char["avatar"] = "default_avatar.png"

            
            # Set optional fields to null if they're empty strings or empty lists
            optional_fields = ['backstory', 'faction', 'skills', 'equipment']
            for field in optional_fields:
                if field in char and (char[field] == "" or char[field] == []):
                    char[field] = None
    
    # Fix relationship_changes - ensure all values are integers only
    if 'relationship_changes' in result_dict:
        fixed_relationship_changes = {}
        for char_id, change_value in result_dict['relationship_changes'].items():
            if isinstance(change_value, dict):
                # If it's a dict, extract the relationship_level change or default to 0
                if 'relationship_level' in change_value:
                    fixed_relationship_changes[char_id] = validate_numeric_range(
                        change_value['relationship_level'], -10, 10, 0
                    )
                else:
                    fixed_relationship_changes[char_id] = 0
            elif isinstance(change_value, (int, float)):
                fixed_relationship_changes[char_id] = validate_numeric_range(
                    change_value, -10, 10, 0
                )
            else:
                # Default to 0 for any other type
                fixed_relationship_changes[char_id] = 0
        result_dict['relationship_changes'] = fixed_relationship_changes
    
    # Fix game_state structure
    if 'game_state' in result_dict:
        gs = result_dict['game_state']
        
        # Ensure environmental_conditions exists
        if 'environmental_conditions' not in gs:
            gs['environmental_conditions'] = {
                "weather": "clear",
                "visibility": "normal", 
                "temperature": "comfortable",
                "hazard_level": 0
            }
        else:
            gs['environmental_conditions']['hazard_level'] = validate_numeric_range(
                gs['environmental_conditions'].get('hazard_level', 0), 0, 10, 0
            )
        
        # Ensure resource_availability exists
        if 'resource_availability' not in gs:
            gs['resource_availability'] = {
                "food": "moderate",
                "water": "moderate",
                "medical_supplies": "scarce",
                "shelter_materials": "moderate",
                "fuel": "scarce",
                "tools": "moderate"
            }
        
        # Fix active_objectives
        if 'active_objectives' in gs:
            for obj in gs['active_objectives']:
                obj['progress'] = validate_numeric_range(obj.get('progress', 0), 0, 100, 0)
                obj['escalation_level'] = validate_numeric_range(obj.get('escalation_level', 1), 1, 10, 1)
                
                # Set optional fields to null
                if 'rewards' in obj:
                    if not isinstance(obj['rewards'], list) or obj['rewards'] == []:
                        obj['rewards'] = None

                if 'time_limit' in obj and (obj['time_limit'] == "" or obj['time_limit'] == "None"):
                    obj['time_limit'] = None
    
    # Fix inventory items
    if 'current_inventory' in result_dict:
        for item in result_dict['current_inventory']:
            if 'durability' in item:
                item['durability'] = validate_numeric_range(item['durability'], 0, 100, 100)
    
    # Fix threat_updates
    if 'threat_updates' in result_dict:
        for threat in result_dict['threat_updates']:
            threat['escalation_level'] = validate_numeric_range(
                threat.get('escalation_level', 1), 1, 10, 1
            )
    
    # Fix discovered_lore
    if 'discovered_lore' in result_dict:
        valid_categories = ['history', 'character', 'location', 'faction', 'event', 'artifact']
        for lore in result_dict['discovered_lore']:
            if 'category' in lore and lore['category'] not in valid_categories:
                lore['category'] = 'history'
            if 'discovered_at' not in lore or not lore['discovered_at']:
                lore['discovered_at'] = datetime.now().isoformat() + 'Z'
            lore['importance_level'] = validate_numeric_range(
                lore.get('importance_level', 1), 1, 10, 1
            )
    
    # Fix location_details
    if 'location_details' in result_dict:
        ld = result_dict['location_details']
        ld['safety_level'] = validate_numeric_range(ld.get('safety_level', 5), 1, 10, 5)
        
        # Ensure arrays exist
        for field in ['exits', 'hidden_areas', 'resource_nodes']:
            if field not in ld:
                ld[field] = []
    
    # Fix world_info - ensure it has proper structure
    if 'world_info' in result_dict:
        wi = result_dict['world_info']
        
        # Convert complex objects to simple strings if needed
        for field in ['key_locations', 'dominant_factions', 'major_threats']:
            if field in wi and isinstance(wi[field], list):
                # Convert dict objects to strings
                wi[field] = [
                    item['name'] if isinstance(item, dict) and 'name' in item else str(item)
                    for item in wi[field]
                ]
        
        # Fix historical_timeline - ensure it's a list of dicts
        if 'historical_timeline' in wi:
            if isinstance(wi['historical_timeline'], dict):
                # Convert single dict to list of dicts
                original_dict = wi['historical_timeline']
                wi['historical_timeline'] = [original_dict]
            elif not isinstance(wi['historical_timeline'], list):
                # Default to empty list if not a list
                wi['historical_timeline'] = []
        
        # Ensure required fields exist
        required_wi_fields = ['name', 'theme', 'description', 'key_locations', 'dominant_factions', 'major_threats', 'cultural_notes', 'historical_timeline']
        for field in required_wi_fields:
            if field not in wi:
                if field in ['key_locations', 'dominant_factions', 'major_threats', 'cultural_notes', 'historical_timeline']:
                    wi[field] = []
                else:
                    wi[field] = f"Default {field}"
    
    # Fix interactive_elements
    if 'interactive_elements' in result_dict:
        for elem in result_dict['interactive_elements']:
            if 'side_quest_trigger' in elem and (elem['side_quest_trigger'] == {} or elem['side_quest_trigger'] == ""):
                elem['side_quest_trigger'] = None
    
    # Ensure all required top-level fields exist
    # Fix inventory_changes structure
    if 'inventory_changes' not in result_dict or not isinstance(result_dict['inventory_changes'], dict):
        result_dict['inventory_changes'] = {
            "added_items": [],
            "removed_items": [],
            "modified_items": []
        }
    else:
        ic = result_dict['inventory_changes']
        for field in ['added_items', 'removed_items', 'modified_items']:
            if field not in ic or not isinstance(ic[field], list):
                ic[field] = []

    required_fields = [
        'scene_tag', 'location', 'world', 'narration_text', 'dialogue', 'characters',
        'options', 'game_state', 'inventory_changes', 'current_inventory',
        'mood_atmosphere', 'history_entry', 'relationship_changes', 'new_secrets',
        'new_objectives', 'completed_objectives_this_scene', 'interactive_elements',
        'environmental_discoveries', 'threat_updates', 'ambient_events',
        'discovered_lore', 'world_info', 'location_details'
    ]
    
    for field in required_fields:
        if field not in result_dict:
            if field in ['dialogue', 'characters', 'options', 'new_secrets', 'new_objectives', 
                        'completed_objectives_this_scene', 'interactive_elements', 
                        'environmental_discoveries', 'threat_updates', 'ambient_events', 'discovered_lore']:
                result_dict[field] = []
            elif field in ['relationship_changes']:
                result_dict[field] = {}
            elif field == 'mood_atmosphere':
                result_dict[field] = 'neutral'
            else:
                result_dict[field] = f"default_{field}"

    # Ensure current_inventory contains valid Item dicts
    if 'current_inventory' in result_dict:
        fixed_inventory = []
        for item in result_dict['current_inventory']:
            if isinstance(item, str):
                # Minimal valid fallback for string items
                fixed_inventory.append({
                    "name": item,
                    "quantity": 1,
                    "description": f"A mysterious item named {item}.",
                    "durability": 100,
                    "item_type": "misc",
                    "properties": {}
                })
            elif isinstance(item, dict):
                # Fill missing fields with defaults
                item.setdefault("name", "unknown_item")
                item.setdefault("quantity", 1)
                item.setdefault("description", f"No description for {item.get('name', 'unknown')}")
                item["durability"] = validate_numeric_range(item.get("durability", 100), 0, 100, 100)
                item.setdefault("item_type", "misc")
                item.setdefault("properties", {})
                fixed_inventory.append(item)
        result_dict['current_inventory'] = fixed_inventory

    if 'inventory_changes' in result_dict:
        for key in ['added_items', 'removed_items', 'modified_items']:
            if key in result_dict['inventory_changes']:
                fixed_items = []
                for item in result_dict['inventory_changes'][key]:
                    if isinstance(item, str):
                        fixed_items.append({
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
                        fixed_items.append(item)
                result_dict['inventory_changes'][key] = fixed_items

    # Fix relationships mapping to ensure all values are valid integers between -10 and 10
    if 'game_state' in result_dict and 'relationships' in result_dict['game_state']:
        fixed_relationships = {}
        for char_id, val in result_dict['game_state']['relationships'].items():
            try:
                # Attempt to convert string like "0/10" to int — fallback to 0
                fixed_val = int(val)
            except (ValueError, TypeError):
                # Try to extract int from format like "0/10"
                if isinstance(val, str) and "/" in val:
                    try:
                        fixed_val = int(val.split("/")[0].strip())
                    except:
                        fixed_val = 0
                else:
                    fixed_val = 0
            # Clamp value to range
            fixed_val = max(-10, min(10, fixed_val))
            fixed_relationships[char_id] = fixed_val
        result_dict['game_state']['relationships'] = fixed_relationships

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
    json_str = json_str.replace("“", '"').replace("”", '"').replace("‘", "'").replace("’", "'")

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
