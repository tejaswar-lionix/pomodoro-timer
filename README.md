# pomodoro-timer

Plan pomodoro sessions and keep a session log.

## Usage

```bash
python3 -c "from timer import *; print(format_seconds(1500)); print(plan_session(2))"
```

## Features

- Session planning with work and break blocks
- Readable mm:ss formatting
- CSV logging with log_session(path, kind, seconds)

## Tests

```bash
python3 -m unittest -q
```

## License

MIT
