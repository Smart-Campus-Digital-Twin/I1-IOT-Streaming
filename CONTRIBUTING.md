# Contributing

This project follows a lightweight agile workflow. Everything starts with an issue, moves through a branch, and lands via a reviewed pull request.

---

## Workflow Overview

```
Issue (backlog)
  └── Branch from main
        └── Commits (small, focused)
              └── Pull Request
                    └── Review + approve
                          └── Squash merge to main
```

---

## Issues

### When to open one
Open an issue for **everything** — bug, feature, chore, question. No direct commits to `main` without a linked issue.

### Issue types and labels

| Label | When to use |
|---|---|
| `bug` | Something is broken or producing wrong data |
| `feature` | New capability or sensor/building addition |
| `chore` | Dependency bump, refactor, infra change |
| `performance` | Throughput, latency, resource usage improvement |
| `security` | Auth, credential, or network hardening |
| `docs` | README, CONTRIBUTING, code comments |
| `question` | Design discussion or clarification needed |

### Issue template (mental model — no file required)
```
Title:   [area] short description   e.g.  [simulator] canteen occupancy pattern off at weekends

What:    One sentence on what is wrong or what should exist.
Why:     Why it matters — data quality, performance, correctness.
Acceptance criteria:
  - [ ] Specific, testable outcome 1
  - [ ] Specific, testable outcome 2
```

### Sizing (story points — add as label)
| Points | Meaning |
|---|---|
| `sp:1` | Trivial — config change, one-liner |
| `sp:2` | Small — single file, clear scope |
| `sp:3` | Medium — a few files, some design |
| `sp:5` | Large — consider splitting |
| `sp:8` | Too big — must be split before starting |

---

## Branches

Branch from `main`. Name your branch using this pattern:

```
<type>/<issue-number>-<short-description>

Examples:
  feature/42-canteen-heat-sensor
  bug/17-occupancy-night-drift
  chore/31-bump-influxdb-client
  security/55-mqtt-tls
  docs/8-readme-ui-guide
```

```bash
git checkout main && git pull
git checkout -b feature/42-canteen-heat-sensor
```

---

## Commits

Keep commits **small and single-purpose**. Each commit should pass if run in isolation.

### Message format
```
<type>: <what changed>  (50 chars max)

Optional body — the WHY, not the what.
Reference the issue: closes #42
```

**Types:** `feat` `fix` `chore` `refactor` `perf` `security` `docs` `test`

**Good examples:**
```
feat: add heat sensor to canteen room topology
fix: occupancy night drift due to UTC vs local time
perf: batch kafka commits every 100 messages
security: add MQTT username/password auth
```

**Avoid:**
```
fixed stuff
WIP
updates
more changes
```

---

## Pull Requests

### Before opening
- [ ] Branch is up to date with `main` (`git rebase main`)
- [ ] All containers start cleanly (`make up && make ps`)
- [ ] Data flows end-to-end (check InfluxDB has recent readings)
- [ ] No leftover debug code or TODO comments meant for cleanup

### PR title
Same format as a commit message — `type: short description`.

### PR description template
```markdown
## What
One paragraph — what this PR does.

## Why
Link to issue: closes #<n>
One sentence on the motivation.

## Changes
- `file/path.py` — what changed and why
- `docker-compose.yml` — new service added: X

## Test checklist
- [ ] `make up` — all containers healthy
- [ ] InfluxDB shows readings for affected sensors
- [ ] No new errors in `docker logs campus-processor`
- [ ] Kafka consumer lag stays near zero
```

### Size rule
A PR that touches more than **5 files unrelated to each other** should be split. Reviewers cannot give useful feedback on a 20-file PR.

---

## Review

### As author
- Respond to every comment — either fix it or explain why not
- Don't push unrelated changes after review starts
- Mark resolved threads as resolved

### As reviewer
- Comment on the **why**, not just the what
- Use these prefixes to signal intent:

| Prefix | Meaning |
|---|---|
| `nit:` | Minor style — author can choose to fix |
| `q:` | Genuine question, not a blocker |
| `suggest:` | Better approach, not a blocker |
| `blocker:` | Must fix before merge |

### Approval rule
- At least **1 approval** required before merge
- Author cannot approve their own PR
- CI must pass (if configured)

---

## Merging

Use **squash merge** for feature and bug branches — keeps `main` history linear and readable.

```
main history after squash merge:
  feat: add canteen occupancy sensor (#42)
  fix: occupancy night drift UTC vs local time (#17)
  perf: batch kafka commits (#31)
```

Use **merge commit** (no squash) only for long-lived release branches.

```bash
# On GitHub: "Squash and merge"
# Locally if needed:
git checkout main
git merge --squash feature/42-canteen-heat-sensor
git commit -m "feat: add canteen heat sensor (#42)"
git push
```

After merge: **delete the branch**.

---

## Sprint Rhythm (suggested)

| Cadence | Activity |
|---|---|
| Start of sprint | Move issues into `in progress`, assign owners |
| During sprint | Daily: check Kafka consumer lag + container health |
| End of sprint | Demo new sensor data in Grafana, close merged issues |
| Backlog grooming | Size and label new issues, split anything `sp:8` |

---

## Quick reference — common workflows

**Fix a bug:**
```bash
git checkout -b bug/17-occupancy-drift
# make changes
git commit -m "fix: occupancy night drift due to UTC vs local time"
# open PR → squash merge → delete branch
```

**Add a new sensor type:**
1. Open `feature` issue with acceptance criteria
2. Add sensor class in `simulator/sensors/`
3. Add to room topology in `simulator/campus/topology.py`
4. Add threshold rule in `analytics/detectors/threshold.py`
5. Rebuild: `docker compose up -d --build simulator analytics`
6. Verify in InfluxDB Data Explorer

**Add a new building:**
1. Open `feature` issue
2. Add to `simulator/campus/topology.py`
3. Add seed row to `infra/postgres/init.sql`
4. Rebuild simulator
5. If postgres volume is live: manually `INSERT INTO buildings ...`
