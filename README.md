# envchain

Lightweight env variable chaining and inheritance manager for multi-stage deployments.

---

## Installation

```bash
pip install envchain
```

Or with Poetry:

```bash
poetry add envchain
```

---

## Usage

Define layered environment configs that inherit and override across stages:

```python
from envchain import EnvChain

chain = EnvChain(base=".env", stages=[".env.staging", ".env.local"])
chain.load()

# Variables are resolved in order: base → staging → local
db_url = chain.get("DATABASE_URL")
debug = chain.get("DEBUG", default="false")
```

You can also export the resolved environment to a flat `.env` file:

```python
chain.export(".env.resolved")
```

To inspect which stage a variable was resolved from, use `chain.source()`:

```python
chain.source("DATABASE_URL")  # returns ".env.staging"
```

**Stage resolution order:** later stages take priority over earlier ones, allowing local overrides without modifying shared configs.

### CLI

```bash
envchain resolve --base .env --stages .env.staging .env.local --output .env.resolved
```

---

## Why envchain?

- ✅ No bloated dependencies
- ✅ Predictable override order
- ✅ Works with Docker, CI/CD pipelines, and local dev
- ✅ Drop-in replacement for `python-dotenv` workflows

---

## License

MIT © envchain contributors
