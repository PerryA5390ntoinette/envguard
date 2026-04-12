# envguard

> Validate and audit `.env` files against a defined schema to catch missing or malformed variables before deployment.

---

## Installation

```bash
pip install envguard
```

Or with pipx for isolated CLI usage:

```bash
pipx install envguard
```

---

## Usage

Define a schema file (`.env.schema`) describing your required variables:

```ini
DATABASE_URL=required,url
PORT=required,integer
DEBUG=optional,boolean
SECRET_KEY=required,min_length:32
```

Then run `envguard` against your `.env` file:

```bash
envguard check --env .env --schema .env.schema
```

**Example output:**

```
✔  DATABASE_URL   valid
✔  PORT           valid
✘  DEBUG          missing (optional — warning only)
✘  SECRET_KEY     too short (got 16 chars, expected ≥ 32)

2 errors, 1 warning. Validation failed.
```

Exit codes: `0` for success, `1` for validation failure — making it easy to integrate into CI pipelines.

```bash
# Use in a CI step
envguard check --env .env --schema .env.schema || exit 1
```

---

## Options

| Flag | Description |
|------|-------------|
| `--env` | Path to the `.env` file (default: `.env`) |
| `--schema` | Path to the schema file (default: `.env.schema`) |
| `--strict` | Treat warnings as errors |
| `--format` | Output format: `text`, `json` |

---

## License

MIT © [envguard contributors](https://github.com/yourname/envguard)