import unittest

from timer import format_seconds, plan_session


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
        self.assertEqual(rows[0], ["kind", "seconds"])
        self.assertEqual(len(rows), 3)


if __name__ == "__main__":
    unittest.main()
