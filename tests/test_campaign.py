import copy
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'backend'))
from fastapi.testclient import TestClient
from models.schemas import Item, InventoryChanges, SceneResponse
from routes import campaign, game
from agents.data_validate_game import validate_and_fix_response
from main import app

class CampaignTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.db = patch.object(campaign, 'DB_PATH', Path(self.temp.name) / 'campaign.db')
        self.db.start()
        self.client = TestClient(app)
        self.scene = validate_and_fix_response({'scene_tag': 'test', 'narration_text': 'Sinbad faces the flood and chooses to protect the city. ' * 5, 'history_entry': 'Sinbad prepared the rescue and learned how to stop the rising flood.', 'ending_summary': 'The rescue ship reached the harbor safely; Elda kept the beacon burning and the villagers rebuilt together.', 'story_plan': {'central_conflict': 'Flood', 'climax': 'Open the gates', 'possible_endings': ['Rescue', 'Evacuate']}})
        self.scene['inventory_changes'] = {'added_items': [], 'removed_items': [], 'modified_items': []}
        self.item = Item(name='Rope', quantity=2, description='Rescue rope', durability=100, item_type='tool', properties={})
        self.input = {
            'session_id': 'test-player', 'scenes_completed': 999, 'player_choice': 'Begin',
            'user_interaction': {'interaction_type': 'narrative_choice', 'choice_text': 'Begin', 'interaction_context': {}},
            'current_location': 'start', 'current_world': 'city', 'scene_tag': 'start', 'present_characters': [],
            'current_scene': {**{k:v for k,v in self.scene.items() if k in __import__('models.schemas', fromlist=['CurrentSceneContext']).CurrentSceneContext.model_fields}, 'narrative_options': []},
            'current_inventory': [], 'game_state': self.scene['game_state'],
            'game_progress': {'scenes_completed': 999, 'play_time_minutes': 0, 'story_escalation_level': 1, 'tension_level': 1, 'major_story_beats': [], 'active_themes': [], 'world_knowledge': {}, 'faction_standings': {}, 'player_preferences': {}, 'preferred_interaction_types': []},
            'recent_history': [], 'agent_hints': {}, 'emergency_flags': {}
        }
    def tearDown(self):
        self.db.stop(); self.temp.cleanup()
    def test_inventory_ledger(self):
        changes = InventoryChanges(added_items=[], removed_items=[self.item.model_copy(update={'quantity': 1})], modified_items=[self.item.model_copy(update={'durability': 70})])
        result = campaign.apply_inventory([self.item], changes)
        self.assertEqual((result[0].quantity, result[0].durability), (1, 70))
        self.assertEqual(self.item.quantity, 2)
        with self.assertRaises(ValueError): campaign.apply_inventory([], changes)
    def test_complete_thirty_turns_and_resume(self):
        self.client.post('/game/init', json={'session_id': 'test-player', 'action': 'new', 'world': 'City', 'total_turns': 30})
        async def generate(*args):
            scene = copy.deepcopy(self.scene)
            if not campaign.load('test-player')['memory']:
                scene['inventory_changes']['added_items'] = [self.item.model_dump()]
            return json.dumps(scene)
        with patch.object(game, 'process_game_turn', generate):
            for turn in range(1, 31):
                response = self.client.post('/game/interact', json=self.input)
                self.assertEqual(response.status_code, 200, response.text)
                data = response.json()
                self.assertEqual(data['game_state']['story_flags']['turn'], turn)
                self.assertEqual(data['current_inventory'][0]['quantity'], 2)
                self.input['scene_tag'] = data['scene_tag']
                self.assertEqual(data['story_plan'], {})
                self.assertEqual(data['game_state']['story_flags']['is_complete'], turn == 30)
            self.assertEqual(data['options'], [])
            self.assertEqual(self.client.post('/game/interact', json=self.input).status_code, 409)
        loaded = self.client.post('/game/init', json={'session_id': 'test-player', 'action': 'load'}).json()
        self.assertEqual(loaded['latest_memory_data']['scenes_completed'], 30)
        self.assertEqual(loaded['latest_memory_data']['inventory'][0]['quantity'], 2)
    def test_narrative_approach_resolves_legacy_active_encounter(self):
        self.client.post('/game/init', json={'session_id': 'test-player', 'action': 'new', 'world': 'City'})
        contexts = []
        async def generate(context, *args):
            contexts.append(context)
            result = copy.deepcopy(self.scene)
            if len(contexts) == 1:
                result['encounter'] = {'id': 'gate', 'kind': 'infiltration', 'title': 'The guarded gate', 'description': 'A patrol blocks the gate.', 'enemy_name': 'Gate patrol'}
            return json.dumps(result)
        with patch.object(game, 'process_game_turn', generate):
            first = self.client.post('/game/interact', json=self.input).json()
            self.assertEqual(first['game_state']['story_flags']['encounter']['status'], 'active')
            self.input['scene_tag'] = first['scene_tag']
            self.input['player_choice'] = 'Ask the keeper to distract the patrol while I open the sluice.'
            second = self.client.post('/game/interact', json=self.input)
        self.assertEqual(second.status_code, 200, second.text)
        self.assertIn('distract the patrol', contexts[-1])
        self.assertEqual(second.json()['game_state']['story_flags']['turn'], 2)
        self.assertIsNone(second.json()['game_state']['story_flags']['encounter'])

    def test_missing_opening_plan_is_repaired_before_saving(self):
        self.client.post('/game/init', json={'session_id': 'test-player', 'action': 'new', 'world': 'City'})
        calls = []
        async def generate(context, *args):
            calls.append(context)
            scene = copy.deepcopy(self.scene)
            if len(calls) == 1:
                scene['story_plan'] = {}
            return json.dumps(scene)
        with patch.object(game, 'process_game_turn', generate):
            result = self.client.post('/game/interact', json=self.input)
        self.assertEqual(result.status_code, 200, result.text)
        self.assertEqual(len(calls), 2)
        self.assertIn('FORMAT CORRECTION', calls[1])
        self.assertEqual(campaign.load('test-player')['memory']['scenes_completed'], 1)
        self.assertEqual(campaign.load('test-player')['plan']['central_conflict'], 'Flood')

    def test_provider_rate_limit_is_actionable_without_spending_turn(self):
        import httpx
        from groq import RateLimitError
        self.client.post('/game/init', json={'session_id': 'test-player', 'action': 'new', 'world': 'City'})
        async def limited(*args):
            raise RateLimitError('limited', response=httpx.Response(429, request=httpx.Request('POST', 'https://api.groq.com')), body=None)
        with patch.object(game, 'process_game_turn', limited):
            response = self.client.post('/game/interact', json=self.input)
        self.assertEqual(response.status_code, 429)
        self.assertEqual(response.headers['retry-after'], '60')
        self.assertIn('free-tier limit', response.json()['detail'])
        self.assertIsNone(campaign.load('test-player')['memory'])

    def test_failed_generation_does_not_advance(self):
        self.client.post('/game/init', json={'session_id': 'test-player', 'action': 'new', 'world': 'City'})
        async def fail(*args): raise RuntimeError('provider unavailable')
        with patch.object(game, 'process_game_turn', fail):
            self.assertEqual(self.client.post('/game/interact', json=self.input).status_code, 502)
        self.assertIsNone(campaign.load('test-player')['memory'])
    def test_exhausted_items_and_modification_cannot_mint_quantity(self):
        changes = InventoryChanges(added_items=[], removed_items=[self.item], modified_items=[])
        self.assertEqual(campaign.apply_inventory([self.item], changes), [])
        changes = InventoryChanges(added_items=[], removed_items=[], modified_items=[self.item.model_copy(update={"quantity": 99})])
        self.assertEqual(campaign.apply_inventory([self.item], changes)[0].quantity, 2)

    def test_relationship_deltas_and_objectives_persist(self):
        from models.schemas import AgentInput, QuestObjective
        source = AgentInput(**self.input)
        source.game_state.relationships = {"keeper": 3}
        quest = QuestObjective(id="beacon", description="Relight the beacon", quest_type="main", completed=False, involves_npcs=[], progress=40, escalation_level=1)
        source.game_state.active_objectives = [quest]
        scene = SceneResponse(**copy.deepcopy(self.scene))
        scene.relationship_changes = {"keeper": 2}
        result = campaign.reconcile(source, scene, 2, 30, {})
        self.assertEqual(result.game_state.relationships["keeper"], 5)
        self.assertIn("beacon", [o.id for o in result.game_state.active_objectives])
        result.completed_objectives_this_scene = ["beacon"]
        result = campaign.reconcile(source, result, 3, 30, {})
        self.assertIn("beacon", result.game_state.completed_objectives)
        self.assertNotIn("beacon", [o.id for o in result.game_state.active_objectives])

    def test_json_preserves_quoted_dialogue(self):
        from agents.data_validate_game import parse_json_block
        data = {"narration_text": 'The keeper said "Go!"\nSinbad nodded.'}
        self.assertEqual(parse_json_block("```json\n" + json.dumps(data, indent=2) + "\n```"), data)

    def test_tactical_actions_do_not_advance_story_and_award_once(self):
        from routes import encounters
        from models.schemas import EncounterSpec
        self.client.post('/game/init', json={'session_id': 'test-player', 'action': 'new', 'world': 'City', 'total_turns': 10})
        async def generate(*args):
            scene = copy.deepcopy(self.scene)
            scene['encounter'] = {'id': 'gate', 'kind': 'combat', 'title': 'Hold the gate', 'description': 'Mara needs a route out.', 'enemy_name': 'Gatekeeper', 'reward': self.item.model_dump()}
            return json.dumps(scene)
        with patch.object(game, 'process_game_turn', generate):
            data = self.client.post('/game/interact', json=self.input).json()
            encounter = data['game_state']['story_flags']['encounter']
            self.assertEqual(self.client.post('/game/interact', json=self.input).status_code, 409)
            for action in ['guard', 'exploit', 'strike', 'exploit', 'strike']:
                if encounter['status'] != 'active': break
                req = {'session_id': 'test-player', 'encounter_id': encounter['id'], 'expected_round': encounter['round'], 'action': action}
                res = self.client.post('/game/encounter', json=req)
                self.assertEqual(res.status_code, 200, res.text)
                snapshot = res.json()['memory']
                encounter = snapshot['game_state']['story_flags']['encounter']
                self.assertEqual(snapshot['scenes_completed'], 1)
                self.assertEqual(self.client.post('/game/encounter', json=req).status_code, 409)
            self.assertEqual(encounter['status'], 'won')
            self.assertEqual(snapshot['inventory'][0]['quantity'], 2)
            self.assertEqual(len(snapshot['game_state']['story_flags']['encounter_history']), 1)

    def test_encounter_items_cost_durability_and_unknown_items_are_rejected(self):
        from routes import encounters
        from models.schemas import EncounterSpec
        spec = EncounterSpec(id='rescue', kind='rescue', title='Save the crew', description='Hold the bridge.', enemy_name='Bridge')
        encounter = encounters.create(spec, 1)
        with self.assertRaises(ValueError): encounters.resolve(encounter, 'item', [], 'Rope')
        result, items = encounters.resolve(encounter, 'item', [self.item.model_dump()], 'Rope')
        self.assertEqual(items[0]['durability'], 80)
        self.assertEqual(items[0]['quantity'], 2)
        self.assertEqual(result['round'], 1)
        self.assertEqual(result['progress'], 18)
        self.assertEqual(encounter['round'], 0)

    def test_all_encounter_types_support_retreat_without_blocking_story(self):
        from routes import encounters
        from models.schemas import EncounterSpec
        for kind in ['combat', 'infiltration', 'rescue']:
            encounter = encounters.create(EncounterSpec(id='test', kind=kind, title='Mission', description='An obstacle.', enemy_name='Obstacle'), 1)
            result, _ = encounters.resolve(encounter, 'retreat', [])
            self.assertEqual(result['status'], 'retreated')
            with self.assertRaises(ValueError): encounters.resolve(result, 'strike', [])

    def test_scene_cache_is_clickable_and_can_only_be_collected_once(self):
        from routes import encounters
        from models.schemas import EncounterSpec
        spec = EncounterSpec(id='cache', kind='infiltration', title='The sealed archive', description='Reach the archive.', enemy_name='Patrol', props=[{'id': 'seal', 'name': 'Council reliquary', 'description': 'A token that proves the council lied.', 'kind': 'cache', 'item': self.item.model_dump()}])
        encounter = encounters.create(spec, 1)
        encounter, inventory = encounters.resolve(encounter, 'prop', [], 'seal')
        self.assertEqual(inventory[0]['name'], 'Rope')
        self.assertEqual(inventory[0]['quantity'], 2)
        self.assertEqual(encounter['used_props'], ['seal'])
        with self.assertRaises(ValueError): encounters.resolve(encounter, 'prop', inventory, 'seal')

    def test_missing_epilogue_cannot_spend_final_turn(self):
        self.client.post('/game/init', json={'session_id': 'test-player', 'action': 'new', 'world': 'City', 'total_turns': 5})
        async def generate(*args):
            scene = copy.deepcopy(self.scene)
            if campaign.load('test-player')['memory'] and campaign.load('test-player')['memory']['scenes_completed'] == 4:
                scene['ending_summary'] = ''
            return json.dumps(scene)
        with patch.object(game, 'process_game_turn', generate):
            for turn in range(1, 5):
                res = self.client.post('/game/interact', json=self.input)
                self.assertEqual(res.status_code, 200, res.text)
                self.input['scene_tag'] = res.json()['scene_tag']
            self.assertEqual(self.client.post('/game/interact', json=self.input).status_code, 502)
            self.assertEqual(campaign.load('test-player')['memory']['scenes_completed'], 4)

    def test_global_generation_quota_is_atomic_and_persistent(self):
        from concurrent.futures import ThreadPoolExecutor
        with patch.dict('os.environ', {'DAILY_AI_CALL_LIMIT': '3'}):
            with ThreadPoolExecutor(max_workers=5) as pool:
                results = list(pool.map(lambda _: campaign.reserve_generation(), range(8)))
            self.assertEqual(sum(results), 3)
            self.assertFalse(campaign.reserve_generation())

    def test_stale_scene_is_rejected_before_another_model_call(self):
        self.client.post('/game/init', json={'session_id': 'test-player', 'action': 'new', 'world': 'City'})
        async def generate(*args): return json.dumps(copy.deepcopy(self.scene))
        with patch.object(game, 'process_game_turn', generate):
            self.assertEqual(self.client.post('/game/interact', json=self.input).status_code, 200)
            self.assertEqual(self.client.post('/game/interact', json=self.input).status_code, 409)
        self.assertEqual(campaign.load('test-player')['memory']['scenes_completed'], 1)

    def test_first_turn_cannot_import_forged_client_state(self):
        self.client.post('/game/init', json={'session_id': 'test-player', 'action': 'new', 'world': 'City'})
        forged = copy.deepcopy(self.input)
        forged['game_state']['story_flags']['forged_flag'] = True
        forged['current_inventory'] = [self.item.model_dump()]
        captured = []
        async def generate(context, user_id):
            captured.append(context)
            return json.dumps(copy.deepcopy(self.scene))
        with patch.object(game, 'process_game_turn', generate):
            response = self.client.post('/game/interact', json=forged)
            self.assertEqual(response.status_code, 200, response.text)
        self.assertNotIn('forged_flag', captured[0])
        self.assertEqual(response.json()['current_inventory'], [])

    def test_json_envelopes_are_repaired_but_ambiguous_scenes_are_rejected(self):
        from agents.data_validate_game import parse_json_block
        scene = {"narration_text": "A coherent scene", "options": ["Choose a side"]}
        self.assertEqual(parse_json_block(json.dumps(json.dumps(scene))), scene)
        self.assertEqual(parse_json_block(json.dumps([scene])), scene)
        with self.assertRaises(ValueError): parse_json_block(json.dumps([scene, scene]))

    def test_malformed_model_output_is_repaired_once_without_spending_extra_turn(self):
        self.client.post('/game/init', json={'session_id': 'test-player', 'action': 'new', 'world': 'City'})
        calls = []
        async def generate(context, user_id):
            calls.append(context)
            return '[]' if len(calls) == 1 else json.dumps(copy.deepcopy(self.scene))
        with patch.object(game, 'process_game_turn', generate):
            response = self.client.post('/game/interact', json=self.input)
        self.assertEqual(response.status_code, 200, response.text)
        self.assertEqual(len(calls), 2)
        self.assertIn('FORMAT CORRECTION', calls[1])
        self.assertEqual(response.json()['game_state']['story_flags']['turn'], 1)
        with campaign.connect() as conn:
            self.assertEqual(conn.execute('SELECT calls FROM generation_usage').fetchone()[0], 2)

    def test_lengths_and_guest_isolation(self):
        self.assertEqual(self.client.post('/game/init', json={'session_id': 'a', 'action': 'new', 'world': 'City', 'total_turns': 100}).status_code, 400)
        self.client.post('/game/init', json={'session_id': 'a', 'action': 'new', 'world': 'City', 'total_turns': 10})
        self.assertIsNone(campaign.load('b'))
        self.assertEqual(campaign.load('a')['total_turns'], 10)

if __name__ == '__main__': unittest.main()
