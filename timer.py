#!/usr/bin/env python3
"""Plan pomodoro sessions and log completed rounds."""
import csv


def format_seconds(total):
    if total < 0:
        raise ValueError("seconds must not be negative")
    minutes, seconds = divmod(total, 60)
    return f"{minutes:02d}:{seconds:02d}"


def plan_session(rounds=4, work=25, short_break=5):
    if rounds < 1:
        raise ValueError("rounds must be at least 1")
    plan = []
    for round_number in range(1, rounds + 1):
        plan.append(("work", work * 60))
        if round_number < rounds:
            plan.append(("short_break", short_break * 60))
    return plan


def log_session(path, kind, seconds):
    """Append a completed session to a CSV log."""
    import os

    new_file = not os.path.exists(path)
    with open(path, "a", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        if new_file:
            writer.writerow(["kind", "seconds"])
        writer.writerow([kind, seconds])
    return path
