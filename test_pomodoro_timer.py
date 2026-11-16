import unittest

from timer import format_seconds, log_session, plan_session, weekly_stats


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


if __name__ == "__main__":
    unittest.main()
