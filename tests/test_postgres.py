"""Optional integration checks against a dedicated, disposable PostgreSQL database."""
import os
import sys
import unittest
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'backend'))
from routes import campaign

@unittest.skipUnless(os.getenv('TEST_DATABASE_URL'), 'Set TEST_DATABASE_URL to a disposable PostgreSQL database')
class PostgresTests(unittest.TestCase):
    def setUp(self):
        self.env = patch.dict(os.environ, {'DATABASE_URL': os.environ['TEST_DATABASE_URL'], 'DAILY_AI_CALL_LIMIT': '3'})
        self.env.start()
        with campaign.connect() as conn:
            conn.execute('CREATE TABLE IF NOT EXISTS generation_usage (day TEXT PRIMARY KEY, calls INTEGER NOT NULL)')
            conn.execute('TRUNCATE campaigns, generation_usage')

    def tearDown(self):
        self.env.stop()

    def test_save_update_and_guest_isolation(self):
        campaign.save('guest-a', {'turn': 1, 'name': '海'})
        campaign.save('guest-b', {'turn': 7})
        campaign.save('guest-a', {'turn': 2})
        self.assertEqual(campaign.load('guest-a'), {'turn': 2})
        self.assertEqual(campaign.load('guest-b'), {'turn': 7})
        self.assertIsNone(campaign.load('unknown'))

    def test_transaction_rolls_back_on_failure(self):
        with self.assertRaises(RuntimeError):
            with campaign.connect() as conn:
                conn.execute('INSERT INTO campaigns VALUES (%s, %s)', ('rollback', '{}'))
                raise RuntimeError('abort')
        self.assertIsNone(campaign.load('rollback'))

    def test_concurrent_quota_survives_connections(self):
        with ThreadPoolExecutor(max_workers=8) as pool:
            results = list(pool.map(lambda _: campaign.reserve_generation(), range(12)))
        self.assertEqual(sum(results), 3)
        self.assertFalse(campaign.reserve_generation())
