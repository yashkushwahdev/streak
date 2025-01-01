# 🔥 Automated GitHub Streak Keeper

[![Automated Streak Keeper](https://github.com/yashkushwahdev/streak/actions/workflows/daily-commit.yml/badge.svg)](https://github.com/yashkushwahdev/streak/actions/workflows/daily-commit.yml)

An intelligent, automated GitHub Actions workflow designed to maintain your GitHub contribution graph and streak with **natural, realistic developer activity patterns (strictly 2 to 5 commits per day)**.

---

## 🎲 Realistic Developer Activity & Scheduling

1. **Strict Daily Range (2 to 5 Commits/Day):**
   - The engine is hard-capped to **strictly 2 to 5 commits per day** (never 8 or higher).
   - Most days it will perform **2, 3, or 4 commits** (and occasionally 5), perfectly emulating real programmer workflow.
   - Once the day's randomized target is reached, all remaining runs for that day are skipped.

2. **Active Daytime & Evening Windows (No robotic 3 AM runs):**
   - Scheduled across 5 active developer time windows throughout the day (09:15 AM to 11:15 PM IST):
     - **Morning:** `~09:15 AM – 09:35 AM IST` (`03:45 UTC`)
     - **Afternoon:** `~01:15 PM – 01:35 PM IST` (`07:45 UTC`)
     - **Evening:** `~05:15 PM – 05:35 PM IST` (`11:45 UTC`)
     - **Prime Coding:** `~08:15 PM – 08:35 PM IST` (`14:45 UTC`)
     - **Night Wrap-up:** `~11:15 PM – 11:35 PM IST` (`17:45 UTC`)

3. **Random Timing Jitter (Unpredictable Minutes & Seconds):**
   - Each run applies a **random sleep jitter (30s – 15min)**, ensuring commits occur at varied, organic timestamps rather than exact clock minutes.

4. **Streak Safety Guarantee:**
   - If the day is ending and remaining windows equal the needed commits to hit the target, it guarantees execution so your streak is never broken.

---

## 📋 Essential GitHub Account Setup

For commits made by GitHub Actions to count towards your profile streak and contribution graph:

### 1. 📧 Email Associated with GitHub Account
GitHub credits commits strictly by author email:
- Go to [GitHub Email Settings](https://github.com/settings/emails).
- Ensure your email (`yashkushwahdev@gmail.com`) is listed and **verified**.

### 2. 🔐 Workflow Write Permissions
1. Go to this repository's **Settings** -> **Actions** -> **General**.
2. Scroll down to **Workflow permissions**.
3. Select **Read and write permissions** and click **Save**.

### 3. 👁️ Contribution Graph Visibility (For Private Repos)
If this repository is private:
1. Go to your [GitHub Profile Settings](https://github.com/settings/profile).
2. Under **Contributions & Activity**, check **Include private contributions on my profile**.

---

## 🚀 Manual Run
To manually trigger a commit right now:
1. Go to the [Actions tab](https://github.com/yashkushwahdev/streak/actions/workflows/daily-commit.yml).
2. Click **Automated Streak Keeper** in the left sidebar.
3. Click **Run workflow** -> Select `main` -> Click **Run workflow**.

---

## 📄 Activity Record
- View current status in [`last_run.txt`](last_run.txt).
- View structured progress in [`activity_state.json`](activity_state.json).
