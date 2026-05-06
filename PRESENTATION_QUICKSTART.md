# 📋 PRESENTATION PACKAGE: Quick Start

## What You Got
✅ **5 complete presentation scripts** (~5 min 30 sec total)  
✅ **1 master guide** with timing, visuals checklist, Q&A prep  
✅ **Speaker notes** in every script (what to say, what to show, when to pause)  
✅ **Embedded references** to code files and architecture concepts  

---

## Files Created

```
PRESENTATION_SCRIPT_01_INTRO.md              (45 sec)
PRESENTATION_SCRIPT_02_ARCHITECTURE.md       (75 sec)
PRESENTATION_SCRIPT_03_DATA_MODEL.md         (75 sec)
PRESENTATION_SCRIPT_04_ANOMALY_DETECTION.md  (75 sec)
PRESENTATION_SCRIPT_05_INSIGHTS_DEMO.md      (60 sec)
PRESENTATION_MASTER_GUIDE.md                 (Everything tied together)
```

---

## How To Use Right Now

### Option A: Read & Speak (Classic)
1. Open `PRESENTATION_SCRIPT_01_INTRO.md`
2. Read the **MAIN SCRIPT** section aloud (45 seconds)
3. When you reach the **TRANSITION TO NEXT SCRIPT** line, click to Script 02
4. Repeat for Scripts 03–05

### Option B: Show & Tell (With Visuals)
1. Follow the **SPEAKER NOTES** table in each script
2. Use the **VISUAL AIDS** section to know what slides/diagrams you need
3. Demo the live system:
   - Open Grafana at `http://localhost:3000` (occupancy dashboard)
   - Open `graphify-out/graph.html` in a browser
   - Have PostgreSQL ready for alert queries (optional)

### Option C: Print & Present
1. Print `PRESENTATION_MASTER_GUIDE.md` (1 page for timing reference)
2. Print all 5 scripts (5 pages, numbered 1–5)
3. Use as speaker notes while presenting slides in PowerPoint/Google Slides/PDF

---

## What Each Script Contains

| Script | What's Included | Why It Matters |
|--------|-----------------|----------------|
| 1 | Problem + scope | Hook the audience (160 sensors = big problem) |
| 2 | C4 architecture | Show how it's *built* (MQTT → Kafka → Storage) |
| 3 | SensorReading model | Explain the *contract* (why data model matters) |
| 4 | Z-score + alerts | Reveal the *intelligence* (how anomalies are caught) |
| 5 | Dashboards + graph | Show the *payoff* (real insights + architecture) |

---

## Key Visuals You'll Need

### Before You Present
- [ ] C4 Container diagram (draw from Script 2 section)
- [ ] JSON example of SensorReading (copy from Script 3)
- [ ] Time-series chart with a spike (from Grafana or mockup)
- [ ] graph.html file tested in browser

### Nice-to-Have
- [ ] Campus building map or photos
- [ ] "1,920 readings per minute" stat card
- [ ] Alert threshold rules table

### Live Demos (if time allows)
- [ ] Grafana occupancy dashboard
- [ ] graph.html node graph (hover to see edges)
- [ ] PostgreSQL alert_events query

---

## Pro Tips

**🎯 The Story Arc**
- Script 1: "Here's the problem"
- Script 2: "Here's how we solve it"
- Script 3: "This is the heart of the solution"
- Script 4: "This is where the magic happens"
- Script 5: "Here's what we can do with it"

**⏱️ Timing**
- You have **30 seconds of buffer**
- If you go slow (emphasize big ideas), you'll hit 5 min exactly
- If you rush, you'll finish at 4:50 (that's fine)
- If you're 30+ sec over, trim Script 2 or Script 4

**💡 The Five "God Nodes" to Mention**
When someone asks "what's critical," say:
1. `SensorReading` — the data contract
2. `BaseSensor` — the sensor abstraction
3. `MQTTKafkaBridge` — the edge-to-platform gateway
4. `PostgresWriter` — the persistent source of truth
5. `ZScoreDetector` — the brain that catches anomalies

**🎤 Practice Aloud**
- Read all 5 scripts out loud (not silently) once before presenting
- Time yourself (most people go slower when nervous, so +30 sec is normal)
- Identify the 2–3 sentences you find hardest to say and practice those

---

## Quick Reference: God Nodes

From the graphify analysis, these 5 components are the **pillars** of the system:

```
SensorReading (15 edges)
└─ Used by: simulator, bridge, processor, analytics, alerts

BaseSensor (13 edges)
└─ Inherited by: TemperatureSensor, HumiditySensor, OccupancySensor, etc.

MQTTKafkaBridge (10 edges)
└─ Validates & forwards: MQTT campus/* → Kafka sensors.*

PostgresWriter (10 edges)
└─ Persists: sensor metadata, alerts, historical readings

ZScoreDetector (9 edges)
└─ Produces: anomaly alerts based on statistical outliers
```

Mention these in your closing if you want to sound authoritative.

---

## Common Questions (Your Answers)

**"How fast are alerts generated?"**  
→ "End-to-end, under 100 milliseconds. Sensor → MQTT → Kafka → detector → database."

**"What if a sensor fails?"**  
→ "Each reading has a quality score. If quality drops, we flag it as degraded. Downstream services respect that."

**"Can you scale to 1,000 sensors?"**  
→ "Yes. Kafka partitions naturally. InfluxDB handles high cardinality. The architecture doesn't change."

**"What's next?"**  
→ "Predictive analytics. Instead of detecting problems, we'll predict them. The foundation is ready."

---

## Delivery Checklist

Before you stand up to present:

- [ ] Read all 5 scripts aloud (timing check)
- [ ] Know the 3 key takeaways from each script
- [ ] Have C4 diagram ready (on screen or printed)
- [ ] Have graph.html tested and opened in a browser tab
- [ ] Optional: Have Grafana running (make up in repo root)
- [ ] Optional: Have the JSON example ready to paste/show
- [ ] Print the PRESENTATION_MASTER_GUIDE.md (for reference during Q&A)
- [ ] Practice saying the 5 "god nodes" smoothly (don't stumble on names)

---

## If You Get Nervous

Remember:
- You've built/studied this system (or your team did)
- The architecture is solid
- The data is real
- You have 5 short scripts to follow (not memorized, not improvised)
- Pause whenever you need to (audiences don't mind silence)
- Take a breath before each script transition

You've got this. 🚀

---

## Questions?
If you need to adjust timing, cut sections, or add a demo, just edit the relevant script file. All 5 scripts are standalone, but the transitions tie them together.

**Good luck with your presentation!**
