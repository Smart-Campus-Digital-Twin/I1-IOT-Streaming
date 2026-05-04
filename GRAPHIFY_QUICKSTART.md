# Graphify Integration - Quick Reference

## Installation Status ✅ COMPLETE

```
✅ graphifyy v0.7.5 installed in Python venv
✅ VS Code Copilot Chat configured
✅ .graphifyignore created (excludes build artifacts)
✅ .gitignore updated (skips manifest.json, cost.json)
✅ Documentation created (2 comprehensive guides)
✅ GitHub integration file configured
✅ All changes committed to git
```

---

## 🎯 Next Step: Generate the Graph

In **VS Code Copilot Chat**, type:

```
/graphify .
```

**What it does:**
- Extracts code structure (Python, TypeScript, YAML, SQL) — local, no API calls
- Analyzes documentation (markdown, diagrams) — via Claude LLM
- Builds knowledge graph with relationships
- Generates interactive visualization + queryable JSON

**Time:** 1–2 minutes  
**Output location:** `graphify-out/` in repo root

---

## 📊 Outputs You'll Get

| File | Purpose | Commit to Git? |
|------|---------|---|
| `graph.html` | Interactive node visualization | ✅ YES |
| `GRAPH_REPORT.md` | Summary + god nodes + suggestions | ✅ YES |
| `graph.json` | Persistent queryable graph | ✅ YES |
| `cache/` | Speed up re-runs | ⚠️ Optional |
| `manifest.json` | mtime tracking (breaks on clone) | ❌ NO |
| `cost.json` | API costs (local only) | ❌ NO |

---

## 📚 Documentation Created

1. **GRAPHIFY_GUIDE.md** — Complete user manual
   - Quick start (3 steps)
   - All commands + examples
   - File configuration
   - Team workflow
   - Verification checklist
   - Troubleshooting

2. **GRAPHIFY_IMPLEMENTATION.md** — Implementation summary
   - What was installed
   - What will be extracted
   - Expected god nodes & connections
   - Privacy model
   - Benefits overview

3. **.github/copilot-instructions.md** — VS Code integration
   - Auto-reads GRAPH_REPORT.md
   - Triggers for graph queries
   - Integration instructions

---

## 🔍 What Graphify Extracts from I1-IOT-Streaming

### Code Files (Local AST — No API Calls)
```
simulator/     → Sensors, topology, campus buildings
ingestion/     → MQTT→Kafka bridge
processor/     → Writers (InfluxDB, PostgreSQL, hourly aggregator)
analytics/     → Detectors, suppressors, alerts
shared/        → Models, logging
infra/         → Mosquitto, Prometheus, PostgreSQL configs
frontend/      → Next.js, React, Three.js components
```

### Expected God Nodes (Most-Connected)
```
Kafka          → Central event stream
Sensor         → Base type for 160 campus sensors
Alert          → Detector outputs → Suppressor inputs
PostgreSQL     → Sensor registry & metadata
Redis          → Alert cooldown, analytics state
Mosquitto      → MQTT ingestion entry point
```

### Surprising Connections
- `temperature.py` (sensor) ↔ `threshold.py` (detector) via topology
- `occupancy.py` (sensor) ↔ Frontend 3D dashboard via InfluxDB→Grafana
- `docker-compose.yml` ↔ `analytics/main.py` via Kafka topics

---

## 💡 Key Commands

| Action | Command |
|--------|---------|
| Generate | `/graphify .` |
| Update after code changes | `/graphify . --update` |
| Query | `/graphify query "how do sensors connect to alerts?"` |
| Find path | `/graphify path "nodeA" "nodeB"` |
| Explain concept | `/graphify explain "Sensor"` |
| Export to wiki | `/graphify . --wiki` |
| Auto-rebuild on commit | `graphify hook install` |

---

## 🔐 Privacy & Architecture

**Stays Local (No API Calls):**
- Python files (via tree-sitter AST)
- YAML configs
- SQL schemas
- TypeScript/JavaScript
- Import relationships

**Sent to Claude API (LLM Processing):**
- Markdown documentation
- PDFs
- Images
- Semantic extraction only

**Storage:**
- `graph.json` stored locally only
- Team shares via git
- No cloud storage, no telemetry

---

## 📋 Verification Checklist

After running `/graphify .`:

- [ ] `graphify-out/` directory created
- [ ] `graph.html` loads in browser with interactive visualization
- [ ] `GRAPH_REPORT.md` contains god nodes section
- [ ] `graph.json` exists (persistent graph)
- [ ] Can query: `/graphify query "..."`
- [ ] Can find paths: `/graphify path "nodeA" "nodeB"`

---

## 📖 Full Documentation

See **GRAPHIFY_GUIDE.md** in repo root for:
- Complete command reference
- Team workflow setup
- Advanced exports (wiki, SVG, GraphML, Neo4j)
- Automation via git hooks
- Troubleshooting guide

---

## ✨ Benefits

✅ **Single queryable graph** for entire codebase  
✅ **Persistent** — reuse graph.json weeks later  
✅ **Team-shareable** — committed to git  
✅ **Auto-updating** — git hooks (AST-only, no API cost)  
✅ **IDE integration** — VS Code reads graph by default  
✅ **Exportable** — wiki, SVG, GraphML, Obsidian, Neo4j  
✅ **Privacy-first** — code stays local, docs optional LLM  

---

## 🚀 You're All Set!

1. Open VS Code
2. Open Copilot Chat panel
3. Type: `/graphify .`
4. Wait 1–2 minutes
5. Review: `graphify-out/GRAPH_REPORT.md`
6. Query: `/graphify query "architecture question"`
7. Commit: `git add graphify-out/{graph.html,graph.json,GRAPH_REPORT.md}` && `git commit`

**Questions?** See GRAPHIFY_GUIDE.md or run `/graphify --help`

Happy graphing! 🎉
