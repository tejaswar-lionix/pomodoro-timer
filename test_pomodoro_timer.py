import unittest

from timer import (
    format_plan,
    format_seconds,
    log_session,
    plan_session,
    session_total,
    weekly_stats,
)


class TimerTests(unittest.TestCase):
    def test_format_seconds(self):
        self.assertEqual(format_seconds(0), "00:00")
        self.assertEqual(format_seconds(65), "01:05")
        self.assertEqual(format_seconds(1500), "25:00")

    def test_format_rejects_negative(self):
        with self.assertRaises(ValueError):
            format_seconds(-1)

    def test_plan_session_alternates_work_and_breaks(self):
        self.assertEqual(
            plan_session(rounds=2, work=25, short_break=5),
            [("work", 1500), ("short_break", 300), ("work", 1500)],
        )

    def test_plan_requires_rounds(self):
        with self.assertRaises(ValueError):
            plan_session(rounds=0)

    def test_format_plan_numbers_each_block(self):
        self.assertEqual(
            format_plan([("work", 1500), ("short_break", 300)]),
            "1. work 25:00\n2. short_break 05:00",
        )

    def test_format_plan_of_empty_plan(self):
        self.assertEqual(format_plan([]), "No sessions.")

    def test_session_total_sums_plan(self):
        self.assertEqual(
            session_total(plan_session(rounds=2, work=25, short_break=5)),
            3300,
        )

    def test_session_total_of_empty_plan(self):
        self.assertEqual(session_total([]), 0)


class SessionLogTests(unittest.TestCase):
    def test_log_session_writes_header_once(self):
        import csv
        import os
        import tempfile

        from timer import log_session

        with tempfile.TemporaryDirectory() as directory:
            path = os.path.join(directory, "sessions.csv")
            log_session(path, "work", 1500)
            log_session(path, "short_break", 300)
            with open(path, encoding="utf-8") as handle:
                rows = list(csv.reader(handle))
        self.assertEqual(rows[0], ["kind", "seconds", "date"])
        self.assertEqual(len(rows), 3)

    def test_log_session_uses_explicit_day(self):
        import csv
        import os
        import tempfile

        from timer import log_session

        with tempfile.TemporaryDirectory() as directory:
            path = os.path.join(directory, "sessions.csv")
            log_session(path, "work", 1500, day="2026-11-10")
            with open(path, encoding="utf-8") as handle:
                rows = list(csv.reader(handle))
        self.assertEqual(rows[1], ["work", "1500", "2026-11-10"])


class WeeklyStatsTests(unittest.TestCase):
    def test_counts_only_work_in_last_seven_days(self):
        import datetime
        import os
        import tempfile

        from timer import log_session, weekly_stats

        with tempfile.TemporaryDirectory() as directory:
            path = os.path.join(directory, "sessions.csv")
            log_session(path, "work", 1500, day="2026-11-10")
            log_session(path, "work", 1500, day="2026-11-10")
            log_session(path, "short_break", 300, day="2026-11-10")
            log_session(path, "work", 600, day="2026-11-05")
            log_session(path, "work", 1500, day="2026-11-03")
            stats = weekly_stats(path, today=datetime.date(2026, 11, 11))
        self.assertEqual(
            stats,
            {
                "2026-11-10": {"work_minutes": 50.0, "rounds": 2},
                "2026-11-05": {"work_minutes": 10.0, "rounds": 1},
            },
        )

    def test_skips_old_two_column_rows(self):
        import os
        import tempfile

        from timer import weekly_stats

        with tempfile.TemporaryDirectory() as directory:
            path = os.path.join(directory, "sessions.csv")
            with open(path, "w", encoding="utf-8") as handle:
                handle.write("kind,seconds\nwork,1500\n")
                handle.write("kind,seconds,date\nwork,600,2026-11-10\n")
            stats = weekly_stats(path, today="2026-11-11")
        self.assertEqual(stats, {"2026-11-10": {"work_minutes": 10.0, "rounds": 1}})


class SummaryTests(unittest.TestCase):
    def test_summary_counts_mixed_rows(self):
        import os
        import tempfile

        from timer import log_session, summary

        with tempfile.TemporaryDirectory() as directory:
            path = os.path.join(directory, "sessions.csv")
            log_session(path, "work", 1500, day="2026-11-10")
            log_session(path, "work", 600, day="2026-11-11")
            log_session(path, "short_break", 300, day="2026-11-11")
            self.assertEqual(
                summary(path),
                {
                    "work_minutes": 35.0,
                    "work_sessions": 2,
                    "break_sessions": 1,
                    "total_sessions": 3,
                },
            )

    def test_summary_accepts_legacy_two_column_rows(self):
        import os
        import tempfile

        from timer import summary

        with tempfile.TemporaryDirectory() as directory:
            path = os.path.join(directory, "sessions.csv")
            with open(path, "w", encoding="utf-8") as handle:
                handle.write("kind,seconds\nwork,1200\nshort_break,300\n")
                handle.write("kind,seconds,date\nwork,600,2026-11-10\n")
            self.assertEqual(
                summary(path),
                {
                    "work_minutes": 30.0,
                    "work_sessions": 2,
                    "break_sessions": 1,
                    "total_sessions": 3,
                },
            )

    def test_summary_of_empty_log_is_zero(self):
        import os
        import tempfile

        from timer import summary

        with tempfile.TemporaryDirectory() as directory:
            path = os.path.join(directory, "sessions.csv")
            open(path, "w", encoding="utf-8").close()
            self.assertEqual(
                summary(path),
                {
                    "work_minutes": 0.0,
                    "work_sessions": 0,
                    "break_sessions": 0,
                    "total_sessions": 0,
                },
            )


class LongBreakPlanTests(unittest.TestCase):
    def test_inserts_long_break_every_interval(self):
        from timer import plan_with_long_breaks, session_total

        plan = plan_with_long_breaks(rounds=8, interval=4)
        kinds = [kind for kind, _ in plan]
        self.assertEqual(kinds.count("long_break"), 1)
        self.assertEqual(kinds[7], "long_break")
        self.assertEqual(session_total(plan), 14700)

    def test_rejects_bad_interval(self):
        from timer import plan_with_long_breaks

        with self.assertRaises(ValueError):
            plan_with_long_breaks(rounds=4, interval=0)


if __name__ == "__main__":
    unittest.main()
