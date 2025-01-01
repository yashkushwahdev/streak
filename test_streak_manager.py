#!/usr/bin/env python3
"""
Unit tests for streak_manager.py
"""

import os
import unittest
from datetime import datetime, timezone
import streak_manager


class TestStreakManager(unittest.TestCase):

    def setUp(self):
        if os.path.exists("test_state.json"):
            os.remove("test_state.json")
        if os.path.exists("test_last_run.txt"):
            os.remove("test_last_run.txt")

    def tearDown(self):
        if os.path.exists("test_state.json"):
            os.remove("test_state.json")
        if os.path.exists("test_last_run.txt"):
            os.remove("test_last_run.txt")

    def test_daily_target_strictly_between_2_and_5(self):
        targets = set()
        for i in range(200):
            state = {}
            fake_now = datetime(2026, 9, 2, 12, 0, tzinfo=timezone.utc)
            state = streak_manager.get_or_init_daily_state(state, fake_now)
            self.assertIn(state["daily_target"], [2, 3, 4, 5])
            self.assertGreaterEqual(state["daily_target"], 2)
            self.assertLessEqual(state["daily_target"], 5)
            targets.add(state["daily_target"])
        self.assertEqual(targets, {2, 3, 4, 5})

    def test_forced_commit(self):
        state = {
            "current_date": "2026-09-02",
            "daily_target": 3,
            "commits_today": 3
        }
        fake_now = datetime(2026, 9, 2, 18, 0, tzinfo=timezone.utc)
        should_commit, reason = streak_manager.decide_commit(state, fake_now, force=True)
        self.assertTrue(should_commit)
        self.assertIn("Forced run", reason)

    def test_daily_target_reached_skips(self):
        state = {
            "current_date": "2026-09-02",
            "daily_target": 3,
            "commits_today": 3
        }
        fake_now = datetime(2026, 9, 2, 11, 0, tzinfo=timezone.utc)
        should_commit, reason = streak_manager.decide_commit(state, fake_now, force=False)
        self.assertFalse(should_commit)
        self.assertIn("Daily limit reached", reason)

    def test_guaranteed_commit_when_slots_low(self):
        # If it's hour 17 (only 1 slot left) and we have 0 commits of target 2
        state = {
            "current_date": "2026-09-02",
            "daily_target": 2,
            "commits_today": 0
        }
        fake_now = datetime(2026, 9, 2, 17, 0, tzinfo=timezone.utc)
        should_commit, reason = streak_manager.decide_commit(state, fake_now, force=False)
        self.assertTrue(should_commit)
        self.assertIn("Guaranteed run", reason)

    def test_date_rollover_resets_counter(self):
        state = {
            "current_date": "2026-09-01",
            "daily_target": 4,
            "commits_today": 4,
            "total_commits": 10
        }
        fake_now = datetime(2026, 9, 2, 3, 0, tzinfo=timezone.utc)
        new_state = streak_manager.get_or_init_daily_state(state, fake_now)
        self.assertEqual(new_state["current_date"], "2026-09-02")
        self.assertEqual(new_state["commits_today"], 0)
        self.assertEqual(new_state["total_commits"], 10)
        self.assertIn(new_state["daily_target"], [2, 3, 4, 5])


if __name__ == "__main__":
    unittest.main()
