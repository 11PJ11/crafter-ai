# Parking Lot

## Pending Features

- `/nw:update` command - auto-update nWave framework from repo without manual install steps

## Configuration Issues

- **update_cli.py hardcoded repo**: Line 201 in `nWave/cli/update_cli.py` hardcodes `github_api.get_latest_release("anthropics", "claude-code")`. Should be configurable via a config file pointing to `https://github.com/nWave-ai/nWave` (currently private/empty repo)
