#!/usr/bin/env python3
"""
Automated GitHub Streak Keeper - Randomization & Decision Engine
Strictly maintains 2 to 5 commits per day during natural programmer working hours.
"""

import os
import sys
import json
import random
import argparse
from datetime import datetime, timezone

STATE_FILE = "activity_state.json"
STATUS_FILE = "last_run.txt"

# 5 Active daytime/evening windows in UTC (09:15 AM to 11:15 PM IST)
# 03:45 UTC (09:15 AM IST), 07:45 UTC (01:15 PM IST), 11:45 UTC (05:15 PM IST), 14:45 UTC (08:15 PM IST), 17:45 UTC (11:15 PM IST)
SCHEDULED_UTC_HOURS = [3, 7, 11, 14, 17]

COMMIT_MESSAGE_TEMPLATES = [
    "chore: streak activity update [{timestamp}]",
    "chore: sync streak log ({commits_today}/{daily_target})",
    "docs: record streak heartbeat [{timestamp}]",
    "chore: update daily activity record [{date}]",
    "refactor: daily activity sync ({commits_today}/{daily_target})",
    "chore: keep streak active [{timestamp}]",
    "chore: automated activity sync [{date}]"
]


def load_state():
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"Warning: Could not read {STATE_FILE} ({e}). Initializing fresh state.")
    return {}


def save_state(state):
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2, ensure_ascii=False)


def get_remaining_slots_today(now_utc):
    current_hour = now_utc.hour
    return sum(1 for h in SCHEDULED_UTC_HOURS if h >= current_hour)


def get_or_init_daily_state(state, now_utc):
    today_str = now_utc.strftime("%Y-%m-%d")
    
    # Check if we need to reset for a new day
    if state.get("current_date") != today_str:
        # Strictly pick a random target between 2 and 5 commits for today (natural programmer distribution)
        # Weights: 2 commits (35%), 3 commits (40%), 4 commits (15%), 5 commits (10%)
        daily_target = random.choices([2, 3, 4, 5], weights=[35, 40, 15, 10])[0]
        
        state["current_date"] = today_str
        state["daily_target"] = daily_target
        state["commits_today"] = 0
        state["daily_history"] = state.get("daily_history", {})
        if "total_commits" not in state:
            state["total_commits"] = 0

    return state


def decide_commit(state, now_utc, force=False):
    commits_today = state.get("commits_today", 0)
    daily_target = state.get("daily_target", 3)
    remaining_slots = get_remaining_slots_today(now_utc)
    needed_commits = daily_target - commits_today

    if force:
        return True, "Forced run (workflow_dispatch or manual trigger)"

    # Hard cap: Never exceed daily target (strictly between 2 and 5 per day)
    if commits_today >= daily_target:
        return False, f"Daily limit reached ({commits_today}/{daily_target} commits today). Skipping."

    if needed_commits <= 0:
        return False, f"Target fulfilled ({commits_today}/{daily_target}). Skipping."

    # Guarantee streak safety: if remaining slots are needed to hit the daily target, commit now
    if remaining_slots <= needed_commits:
        return True, f"Guaranteed run to preserve streak (Remaining slots: {remaining_slots}, Needed: {needed_commits})"

    # Probabilistic roll (~60% chance) to spread commits across available waking hours
    roll = random.random()
    if roll < 0.60:
        return True, f"Probabilistic roll passed (Roll: {roll:.2f} < 0.60, Progress: {commits_today}/{daily_target})"
    else:
        return False, f"Skipped slot for organic spacing (Roll: {roll:.2f} >= 0.60, Slots remaining: {remaining_slots})"


def generate_commit_message(date_str, timestamp_str, commits_today, daily_target):
    template = random.choice(COMMIT_MESSAGE_TEMPLATES)
    return template.format(
        date=date_str,
        timestamp=timestamp_str,
        commits_today=commits_today,
        daily_target=daily_target
    )


def update_status_file(state, now_utc, trigger_event, reason):
    timestamp_utc = now_utc.strftime("%Y-%m-%d %H:%M:%S UTC")
    date_str = state["current_date"]
    commits_today = state["commits_today"]
    daily_target = state["daily_target"]
    total_commits = state["total_commits"]

    status_content = f"""========================================
🔥 GitHub Streak Keeper Activity Record
========================================
Last Activity Date : {date_str}
Last Activity Time : {timestamp_utc}
Triggered By       : {trigger_event}
Daily Progress     : {commits_today} / {daily_target} commits
Total Commits Made : {total_commits}
Decision Reason    : {reason}
Status             : Active & Synced
========================================
"""
    with open(STATUS_FILE, "w", encoding="utf-8") as f:
        f.write(status_content)


def set_github_output(name, value):
    output_file = os.environ.get("GITHUB_OUTPUT")
    if output_file:
        try:
            with open(output_file, "a", encoding="utf-8") as f:
                f.write(f"{name}={value}\n")
            return
        except Exception:
            pass
    print(f"[GITHUB_OUTPUT] {name}={value}")


def main():
    parser = argparse.ArgumentParser(description="Streak Keeper Manager")
    parser.add_argument("--force", action="store_true", help="Force commit regardless of quota")
    parser.add_argument("--event", type=str, default="schedule", help="Event name (schedule/workflow_dispatch)")
    args = parser.parse_args()

    now_utc = datetime.now(timezone.utc)
    state = load_state()
    state = get_or_init_daily_state(state, now_utc)

    is_forced = args.force or (args.event == "workflow_dispatch")
    should_commit, reason = decide_commit(state, now_utc, force=is_forced)

    print(f"[{now_utc.strftime('%Y-%m-%d %H:%M:%S UTC')}] Decision: should_commit={should_commit}")
    print(f"Reason: {reason}")
    print(f"Current Date: {state['current_date']}, Daily Target: {state['daily_target']}, Commits Today: {state['commits_today']}")

    if should_commit:
        state["commits_today"] += 1
        state["total_commits"] = state.get("total_commits", 0) + 1
        state["last_commit_time"] = now_utc.strftime("%Y-%m-%d %H:%M:%S UTC")

        # Record in daily history
        today_str = state["current_date"]
        if "daily_history" not in state:
            state["daily_history"] = {}
        state["daily_history"][today_str] = {
            "target": state["daily_target"],
            "commits": state["commits_today"],
            "last_time": state["last_commit_time"]
        }

        save_state(state)
        update_status_file(state, now_utc, args.event, reason)

        date_str = state["current_date"]
        timestamp_str = now_utc.strftime("%Y-%m-%d %H:%M:%S UTC")
        commit_msg = generate_commit_message(
            date_str, timestamp_str, state["commits_today"], state["daily_target"]
        )

        set_github_output("should_commit", "true")
        set_github_output("commit_message", commit_msg)
        print(f"Generated Commit Message: '{commit_msg}'")
    else:
        # Save state anyway in case new day was initialized
        save_state(state)
        set_github_output("should_commit", "false")
        set_github_output("commit_message", "")
        print("Skipping commit for this run.")


if __name__ == "__main__":
    main()
