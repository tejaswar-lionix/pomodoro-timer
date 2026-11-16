# pomodoro-timer

Plan pomodoro sessions and keep a session log.

## Usage

```bash
python3 -c "from timer import *; print(format_seconds(1500)); print(plan_session(2))"
python3 -c "from timer import *; print(weekly_stats('sessions.csv'))"
```

## Features

- Session planning with work and break blocks
- Readable mm:ss formatting
- CSV logging with dated rows via log_session(path, kind, seconds, day=None)
- Seven-day work totals with weekly_stats(path, today=None)

## Tests

```bash
python3 -m unittest -q
```

## License

MIT
