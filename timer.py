#!/usr/bin/env python3
"""Plan pomodoro sessions and log completed rounds."""
import csv
from datetime import date, timedelta


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


def session_total(plan):
    if not plan:
        return 0
    return sum(seconds for _, seconds in plan)


def format_plan(plan):
    if not plan:
        return "No sessions."
    lines = []
    for index, (kind, seconds) in enumerate(plan, start=1):
        lines.append(f"{index}. {kind} {format_seconds(seconds)}")
    return "\n".join(lines)


def log_session(path, kind, seconds, day=None):
    """Append a completed session to a CSV log."""
    import os

    if day is None:
        stamp = date.today().isoformat()
    elif isinstance(day, date):
        stamp = day.isoformat()
    else:
        stamp = day
    new_file = not os.path.exists(path)
    with open(path, "a", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        if new_file:
            writer.writerow(["kind", "seconds", "date"])
        writer.writerow([kind, seconds, stamp])
    return path


def weekly_stats(path, today=None):
    today = today or date.today()
    if isinstance(today, str):
        today = date.fromisoformat(today)
    window = {(today - timedelta(days=offset)).isoformat() for offset in range(7)}
    stats = {}
    with open(path, newline="", encoding="utf-8") as handle:
        for row in csv.reader(handle):
            if not row or row[0] == "kind" or len(row) < 3:
                continue
            kind, seconds, stamp = row[0], row[1], row[2]
            if kind != "work" or not stamp or stamp not in window:
                continue
            entry = stats.setdefault(stamp, {"work_minutes": 0.0, "rounds": 0})
            entry["work_minutes"] += int(seconds) / 60
            entry["rounds"] += 1
    for entry in stats.values():
        entry["work_minutes"] = round(entry["work_minutes"], 2)
    return stats


def summary(path):
    result = {
        "work_minutes": 0.0,
        "work_sessions": 0,
        "break_sessions": 0,
        "total_sessions": 0,
    }
    try:
        handle = open(path, newline="", encoding="utf-8")
    except FileNotFoundError:
        return result
    with handle:
        for row in csv.reader(handle):
            if not row or row[0] == "kind" or len(row) < 2:
                continue
            kind, seconds = row[0], row[1]
            try:
                seconds = int(seconds)
            except ValueError:
                continue
            result["total_sessions"] += 1
            if kind == "work":
                result["work_sessions"] += 1
                result["work_minutes"] += seconds / 60
            elif "break" in kind:
                result["break_sessions"] += 1
    result["work_minutes"] = round(result["work_minutes"], 2)
    return result
