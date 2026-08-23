# tracker

Personal time tracker (built with Flask + SQLite).

## Quick start (uv)

### 1) Clone and enter the project
```zsh
git clone git@github.com:vitsyrovat/tracker.git
cd tracker
```

### 2) Install uv (if needed)
```zsh
brew install uv
```

### 3) Sync dependencies from lock file
```zsh
uv sync
```

### 4) Run the app from the project
```zsh
uv run track
```

The app starts on `http://127.0.0.1:8000`.

You can also pass Flask host/port/debug options:
```zsh
uv run track --host 0.0.0.0 --port 8001 --debug
```

## Install `track` globally (run from anywhere)

From the project root, install the package as a uv tool:
```zsh
uv tool install --from . personal-tracker
```

Then you can run:
```zsh
track
```

If needed, reinstall after local package changes:
```zsh
uv tool uninstall personal-tracker
uv tool install --from . personal-tracker
```

## Dependency updates (maintainers)

Update and refresh the lock file when dependencies change:
```zsh
uv lock
uv sync
```

Commit both `pyproject.toml` and `uv.lock`.

## Database initialization

No separate setup step is required. The app creates `tracker.db` automatically if it does not exist.

## Interactive python shell

Open shell with app context:
```
uv run flask --app tracker.app shell
```

## Notes

- If port `8000` is busy, use another port, for example: `uv run track --port 8001`.
- To reset local data, stop the app and delete `tracker.db`.
