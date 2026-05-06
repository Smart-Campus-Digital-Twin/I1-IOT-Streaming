# 🎯 PRESENTATION SCRIPT 5: INSIGHTS, DASHBOARDS & GRAPH ANALYSIS
**Duration:** 60 seconds | **Visual:** Live dashboard / graph visualization

---

## MAIN SCRIPT (Read Aloud)

Now, what does all this data *actually* tell us? When we visualize it, patterns emerge.

Here we have a Grafana dashboard showing **real-time occupancy across all campus buildings**. You can see that occupancy in Academic Building spikes between 9am–12pm (lecture hours), drops at lunch, and returns mid-afternoon. Canteen D shows the opposite pattern — quiet in the morning, packed at lunch, empty after 2pm.

This isn't just interesting — it's actionable. Facilities can use this to optimize HVAC scheduling. If we know the canteen will be packed at 12:15pm, we can pre-cool it to 20°C at noon, not 1pm.

But here's something surprising: **when we analyze the relationships between sensors across the system**, we discover that occupancy actually influences temperature readings. More people in a room → higher CO₂ → warmer room. And our anomaly detector catches this correlation.

We generated a **knowledge graph** of the entire system using artificial intelligence. The graph identified the most critical abstractions — the "god nodes" that everything depends on:

1. **SensorReading** — The core data structure. Used by simulator, bridge, processor, analytics.
2. **BaseSensor** — The abstraction for all sensor types (temperature, humidity, occupancy). Ensures consistency.
3. **MQTTKafkaBridge** — The guardian between the edge and the platform. Validates every message.
4. **PostgresWriter** — The authoritative store for history and alerts.
5. **ZScoreDetector** — The statistical brain that catches anomalies humans would miss.

These five components are the **pillars of the system**. If any one breaks, intelligence stops.

Finally — and this is critical — the graph also revealed surprising connections. For example, the anomaly detector and threshold detector both depend on shared data models. That's not a bug — it's a feature. Shared models mean consistency. If you change how SensorReading is validated in one place, all consumers benefit.

That's the power of good architecture.

---

## SPEAKER NOTES

| Timing | What to Do | What to Say |
|--------|-----------|------------|
| **0:00–0:15** | Open Grafana and show a live time-series panel with occupancy data | Narrate as if discovering the pattern: "Look at this — Academics peak at 9am. Canteen peaks at lunch." Point to the three buildings. |
| **0:15–0:30** | Pause on a specific insight: "Facilities can use this to optimize HVAC" | Make it real. Give a concrete business value: "Pre-cool at noon, not 1pm. Save energy." This shows you understand operations. |
| **0:30–0:45** | Open the `graph.html` file in a browser (rotate/zoom to show clusters) | Show the interactive network diagram. Point to a central node like SensorReading. Say: "These lines show dependencies. The more lines, the more critical the component." |
| **0:45–1:00** | Zoom into the "god nodes" list and read them aloud slowly | For each one, give a **1-line role**: SensorReading (the contract), BaseSensor (consistency), MQTTKafkaBridge (validation), PostgresWriter (history), ZScoreDetector (intelligence). |

---

## HOW TO OPEN THE GRAPH
1. **Local:** Navigate to `graphify-out/graph.html` in VS Code
2. **File → Open in Browser** (or `Ctrl+O` → choose file)
3. **Interact:** Click on nodes, drag to pan, scroll to zoom
4. **Inspect:** Hover over a node to see edges and connections

---

## WHAT THE GRAPH SHOWS
- **Nodes:** 241 (classes, functions, concepts, infrastructure)
- **Edges:** 310 (dependencies, relationships, calls)
- **Communities:** 26 (clusters of related code: sensor types, database writers, analytics, docs, etc.)
- **God Nodes (top 5):** SensorReading (15 edges), BaseSensor (13), MQTTKafkaBridge (10), PostgresWriter (10), ZScoreDetector (9)

**Surprising Finding:** Detectors both use SensorReading and AlertEvent from shared.models. This is intentional — the shared layer ensures consistency.

---

## VISUAL AIDS
1. **Grafana Dashboard** (screenshot or live):
   - Time-series panel: Occupancy (Y-axis: people, X-axis: time)
   - Colored lines for Academic A (blue), Admin B (orange), Research C (green), Canteen D (red)
   - Clear peak at 12:30pm for Canteen D
   
2. **Knowledge Graph** (interactive graph.html):
   - Zoom into center: show SensorReading as the central hub
   - Display god nodes in a callout: ranked by edge count
   - Show a "surprising connection" with a highlight, e.g., ZScoreDetector → SensorReading

3. **God Nodes Table:**
   | Rank | Node | Edges | Role |
   |------|------|-------|------|
   | 1 | SensorReading | 15 | Core data contract |
   | 2 | BaseSensor | 13 | Sensor abstraction |
   | 3 | MQTTKafkaBridge | 10 | Edge-to-platform bridge |
   | 4 | PostgresWriter | 10 | Persistent storage |
   | 5 | ZScoreDetector | 9 | Anomaly intelligence |

---

## CALL-TO-ACTION (END OF PRESENTATION)
> "This system is still being built. We have the foundation. The next phase will add predictive analytics — not just detecting problems, but predicting them before they happen. Imagine knowing an HVAC unit will fail 3 days before it breaks. That's what we're building toward. And it's all possible because we designed the data model and architecture **for that future** from day one."

---

## BACKUP DEMO (If Time Allows)
If you have extra time, you can:
1. Open PostgreSQL client and show 1–2 alert_events rows
2. Run a Flux query in InfluxDB: `from(bucket: "sensors") |> range(start: -1h) |> filter(fn: (r) => r._measurement == "occupancy")`
3. Hover over graph nodes and show the edge labels (uses, calls, contains, etc.)

---

## TIMING VALIDATION
- Intro: 45 sec
- Architecture: 75 sec
- Data Model: 75 sec
- Anomaly Detection: 75 sec
- Insights & Demo: 60 sec
- **Total: 330 sec = 5 min 30 sec**
- **Trim buffer:** 30 sec built in (you can cut the "backup demo" or shorten one section by ~1 sentence)

---

## CLOSING WORDS (For After All 5 Scripts)
> "In summary: **160 sensors → MQTT → Kafka → intelligent analytics → real-time alerts → dashboards**. Each layer has a job. Each service is independent. Each data model is a contract. And the whole system is designed to scale. That's the Smart Campus Digital Twin."

**Q&A:** "I'm happy to answer questions. What would you like to know?"
