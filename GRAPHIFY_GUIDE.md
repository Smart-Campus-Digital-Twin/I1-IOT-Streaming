# Graphify Knowledge Graph Setup Guide

## Overview

Graphify is an AI coding assistant skill that converts your codebase into a queryable knowledge graph. It extracts code structure, relationships, documentation, and generates an interactive visualization plus a persistent JSON graph you can query anytime.

**Installed for:** VS Code Copilot Chat

---

## Quick Start

### Step 1: Generate the Graph (VS Code)

In **VS Code Copilot Chat**, type:

```
/graphify .
```

This will:
- Extract all code files (Python, TypeScript, YAML, SQL)
- Parse documentation (markdown, diagrams)
- Identify relationships and god nodes
- Generate `graphify-out/` with interactive graph + report

**Time:** ~1–2 minutes depending on your machine

### Step 2: Review the Report

Open `graphify-out/GRAPH_REPORT.md`:

- **God Nodes** — most-connected concepts (e.g., Kafka, Sensor, Alert, PostgreSQL)
- **Surprising Connections** — unexpected links between components
- **Suggested Questions** — 4–5 questions the graph can answer

### Step 3: Commit & Share

```bash
git add graphify-out/{graph.html,graph.json,GRAPH_REPORT.md,.github/copilot-instructions.md}
git commit -m "docs: add graphify knowledge graph for codebase navigation"
git push
```

Everyone on the team now gets the graph on `git pull`. VS Code reads `GRAPH_REPORT.md` automatically before answering questions.

---

## All Commands

### Build & Extract

| Command | Purpose |
|---------|---------|
| `/graphify .` | Build graph for current folder |
| `/graphify ./docs --update` | Re-extract only changed docs (markdown, PDFs) |
| `/graphify . --cluster-only` | Rerun community detection (no re-extraction) |
| `/graphify . --mode deep` | More aggressive relationship inference |
| `/graphify . --watch` | Auto-sync as files change (background) |
| `/graphify . --no-viz` | Skip HTML, just report + JSON |

### Query & Navigate

| Command | Purpose |
|---------|---------|
| `/graphify query "how do sensors connect to alerts?"` | Ask natural-language questions |
| `/graphify query "..." --dfs` | Query with depth-first search |
| `/graphify path "anomaly.py" "postgres_writer.py"` | Find shortest path between concepts |
| `/graphify explain "Sensor"` | Explain a specific concept |

### Export & Share

| Command | Purpose |
|---------|---------|
| `/graphify . --wiki` | Generate Wikipedia-style markdown docs |
| `/graphify . --svg` | Export as SVG visualization |
| `/graphify . --graphml` | Export for Gephi / yEd |
| `/graphify . --neo4j` | Generate Neo4j cypher scripts |
| `/graphify . --obsidian` | Generate Obsidian vault |

### Automation

| Command | Purpose |
|---------|---------|
| `graphify hook install` | Auto-rebuild on every git commit (AST-only, no API cost) |
| `graphify hook uninstall` | Remove git hooks |
| `graphify check-update ./src` | See which files changed since last run |

---

## File Configuration

### `.graphifyignore`

Located in repo root. Prevents re-processing build artifacts and large folders:

```
node_modules/
frontend/.next/
frontend/.venv/
__pycache__/
*.pyc
```

Edit as needed.

### `.gitignore` Updates

The following are automatically excluded from git (already configured):

```
graphify-out/manifest.json    # mtime-based (breaks on clone)
graphify-out/cost.json        # local API costs only
```

**Commit to git:**
- `graphify-out/graph.html`
- `graphify-out/graph.json`
- `graphify-out/GRAPH_REPORT.md`
- `.github/copilot-instructions.md`

---

## Integration with I1-IOT-Streaming

### What Graphify Will Extract

**Code Files** (local AST — no API calls):
- `simulator/` — sensor types, topology, campus buildings/rooms
- `ingestion/` — MQTT→Kafka bridge
- `processor/` — writers (InfluxDB, PostgreSQL, hourly aggregator)
- `analytics/` — detectors (anomaly, threshold), suppressors, alerts
- `shared/` — models, logging
- `infra/` — Mosquitto config, Prometheus rules, PostgreSQL schema
- `frontend/` — Next.js dashboard, Three.js components

**Docs** (LLM extraction via Claude):
- README.md, CONTRIBUTING.md
- docs/glossary.md, docs/learning-notes-phase-0.md
- Architecture diagrams

### Expected God Nodes (Most-Connected)

- **Kafka** — bridges ingestion → processor → analytics
- **Sensor** — base type for 160 campus sensors
- **Alert** — links detectors → suppressors → output topics
- **PostgreSQL** — sensor registry, metadata
- **Redis** — alert cooldown state, analytics windows
- **Mosquitto** — MQTT entry point

### Expected Surprising Connections

- How `temperature.py` (sensor) connects to `threshold.py` (detector) via topology config
- How `occupancy.py` links to frontend 3D dashboard via InfluxDB → Grafana → Three.js
- How `docker-compose.yml` relates to `analytics/main.py` via Kafka topics and environment setup

---

## Team Workflow

### One-Time Setup (Repository Owner)

```bash
# 1. Generate graph from VS Code Copilot Chat
/graphify .

# 2. Review outputs
cat graphify-out/GRAPH_REPORT.md

# 3. Commit
git add graphify-out/{graph.html,graph.json,GRAPH_REPORT.md}
git commit -m "docs: add graphify knowledge graph"
git push
```

### Team Members (After Pull)

1. Pull the repo — get graph on `git pull`
2. VS Code automatically reads `GRAPH_REPORT.md` before answering questions
3. Query the graph: `/graphify query "how do X and Y connect?"`

### Keep Graph Updated

**For code changes:**
```bash
/graphify . --update
```

**For doc/PDF changes:**
```bash
/graphify ./docs --update
```

**For large refactors:**
```bash
/graphify . --cluster-only
```

### Optional: Git Hook Auto-Rebuild

For automatic graph updates on every commit:
```bash
graphify hook install
```

This adds post-commit and post-checkout hooks. Graph rebuilds instantly (AST-only, no API cost).

---

## Verification Steps

### 1. Check Outputs Exist

```bash
ls -la graphify-out/
# Should show:
#   graph.html
#   GRAPH_REPORT.md
#   graph.json
#   cache/
#   manifest.json
#   cost.json
```

### 2. Open Interactive Graph

Open `graphify-out/graph.html` in any browser:
- Interactive node visualization should load
- Search for concepts (e.g., "Sensor", "Kafka", "Alert")
- Click nodes to see neighbors and relationships

### 3. Review Report

```bash
cat graphify-out/GRAPH_REPORT.md
```

Check sections:
- **God Nodes** — should list Kafka, Sensor, Alert, PostgreSQL, Redis
- **Surprising Connections** — should reveal architecture insights
- **Suggested Questions** — should be answerable by querying the graph

### 4. Test Queries

In VS Code Copilot Chat:

```
/graphify query "how do threshold detectors link to sensor types?"
```

```
/graphify path "anomaly.py" "influx_writer.py"
```

```
/graphify explain "Sensor"
```

### 5. Commit & Test Team Access

```bash
git push
# Team member pulls and verifies:
cat graphify-out/GRAPH_REPORT.md
```

---

## Privacy & Data Flow

- **Code files** (.py, .yaml, .sql): Processed **locally** via tree-sitter. Nothing leaves your machine.
- **Docs/PDFs/images**: Sent to Claude API (via VS Code's authentication). No telemetry.
- **No data stored**: Graph exists only in `graphify-out/graph.json` on your disk.

---

## Troubleshooting

### "No API key found" Error

This happens if running `graphify extract` from CLI without an API key. **Solution:** Use the `/graphify` command from **VS Code Copilot Chat** instead — it uses VS Code's authentication.

### Graph Not Updating

- If code changed, run: `/graphify . --update`
- If large refactor, run: `/graphify . --cluster-only` to rerun clustering
- If in doubt, delete `graphify-out/` and run `/graphify .` fresh

### Large Files Slowing Down Graph

Edit `.graphifyignore`:
```
# Add slow/large folders:
node_modules/
frontend/.next/
frontend/build/
```

Then re-run `/graphify . --update`.

---

## Further Reading

- [Graphify GitHub](https://github.com/safishamsi/graphify)
- [Graphify Documentation](https://github.com/safishamsi/graphify/blob/v7/docs/how-it-works.md)
- [Full Command Reference](https://github.com/safishamsi/graphify#full-command-reference)

---

## Summary

| Action | Command |
|--------|---------|
| Generate graph | `/graphify .` (in VS Code Copilot Chat) |
| Update code extraction | `/graphify . --update` |
| Query the graph | `/graphify query "..."` |
| Auto-rebuild on commit | `graphify hook install` |
| Export to wiki | `/graphify . --wiki` |
| Commit outputs | `git add graphify-out/{graph.html,graph.json,GRAPH_REPORT.md}` |

That's it! 🎉
