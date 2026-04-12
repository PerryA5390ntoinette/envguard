"""Loads .env files into a plain dictionary."""

from pathlib import Path


def parse_env_line(line: str) -> tuple[str, str] | None:
    """Parse a single .env line into a (key, value) pair or None."""
    stripped = line.strip()
    if not stripped or stripped.startswith("#"):
        return None
    if "=" not in stripped:
        return None
    key, _, raw_value = stripped.partition("=")
    key = key.strip()
    value = raw_value.strip()
    # Strip surrounding quotes
    if len(value) >= 2 and value[0] == value[-1] and value[0] in ('"', "'"):
        value = value[1:-1]
    if not key:
        return None
    return key, value


def load_env_file(path: str | Path) -> dict[str, str]:
    """Load a .env file and return a dictionary of key-value pairs."""
    env_path = Path(path)
    if not env_path.exists():
        raise FileNotFoundError(f".env file not found: {env_path}")

    env_vars: dict[str, str] = {}
    with env_path.open(encoding="utf-8") as f:
        for line in f:
            result = parse_env_line(line)
            if result is not None:
                key, value = result
                env_vars[key] = value
    return env_vars
