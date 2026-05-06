# 🚨 PRESENTATION SCRIPT 4: ANOMALY DETECTION & ALERTS
**Duration:** 75 seconds | **Visual:** Before/after chart and algorithm diagram

---

## MAIN SCRIPT (Read Aloud)

The real magic of this system is **real-time anomaly detection**. We use two complementary strategies:

**Strategy 1: Statistical Anomaly Detection (Z-Score)**
For each sensor, we maintain a sliding window of the last N readings. We compute the mean and standard deviation. Then, when a new reading comes in, we ask: *How many standard deviations away from the mean is this value?* If it's 3+ standard deviations away, it's an outlier — we trigger an alert.

Example: Classroom temperature is normally 21–23°C. The mean is 22°C, standard deviation is 0.5°C. If a reading comes in at 28°C, that's 12 standard deviations above the mean. Something's wrong — maybe the radiator valve is stuck open.

**Strategy 2: Hard Threshold Rules**
For some sensors, statistics aren't enough. We define explicit rules: *Temperature must be between 15°C and 35°C. Humidity must be between 10% and 100%. Pressure must be between 980 and 1050 hPa.*

If a reading violates a threshold, we trigger an alert immediately. No sliding window. No statistics. Just: *value < 15°C? Alert.*

**Alert Suppression**
Here's where it gets sophisticated: we **don't** flood you with alerts. If we've already alerted you about a stuck temperature sensor, we don't alert you again for 5 minutes. We call this **alert suppression**. It prevents alarm fatigue.

All alerts get written to PostgreSQL so you can query, filter, and correlate them with other data.

---

## SPEAKER NOTES

| Timing | What to Do | What to Say |
|--------|-----------|------------|
| **0:00–0:20** | Show a normal temperature time-series chart with a spike at the end | Introduce the problem: "We have 1,920 readings per minute. How do we catch the abnormal ones?" Point to the spike. "That spike is our alert." |
| **0:20–0:40** | Display the Z-score formula and explain it verbally, NOT algebraically | Say: "Z-score is just a way to ask: *how weird is this number compared to normal?*" Don't write the formula `(x - μ) / σ`. Instead, give the concrete example (classroom temp, mean 22°C, std 0.5°C). |
| **0:40–0:50** | Show the example: normal range 21–23°C, abnormal reading 28°C | Calculate aloud: "28 minus 22 is 6. 6 divided by 0.5 is 12 standard deviations. **That's a 5-alarm fire.**" Use enthusiasm. |
| **0:50–1:00** | Show a "threshold rules" table with sensor type and (low, high) bounds | Explain: "Sometimes stats are overkill. We just say: *keep temperature between 15 and 35.*" This is simpler and faster. |
| **1:00–1:15** | Display an alert log on-screen with multiple identical alerts, then show it "suppressed" to 1 alert | Explain alert suppression: "We send the first alert. For the next 5 minutes, we ignore duplicates. Prevents your inbox from exploding." Smile. |

---

## ALGORITHMS IN PLAIN LANGUAGE
**Z-Score:**
- Keep a window of recent readings (e.g., 100 readings = ~8 minutes of data)
- Compute average (μ) and spread (σ)
- New reading comes in: is it 3+ standard deviations away?
- If yes → unusual. Trigger alert.
- If no → normal. Continue.

**Threshold:**
- For each sensor type, define (low, high) bounds
- Does reading fall outside bounds?
- If yes → violates rule. Trigger alert immediately.
- If no → within bounds. Continue.

**Suppression:**
- When an alert fires, note the (sensor_id, rule_id, timestamp)
- For 5 minutes, ignore new alerts for that (sensor_id, rule_id)
- After 5 minutes, cooldown expires. Next alert will fire.

---

## RELATED ARCHITECTURES (From Graph Analysis)
The graph reveals important relationships:
- `ZScoreDetector` has **9 edges** — it's a major decision point
- `ThresholdDetector` also connects to `SensorReading`
- Both detectors use the same `AlertEvent` model (defined in shared.models)
- `AlertSuppressor` operates **between** detectors and database writer

This shows the system is **extensible**: new detectors can be added without touching storage.

---

## VISUAL AIDS
1. **Time-series chart** (X: time, Y: temperature, normal band highlighted, spike shown in red)
2. **Z-score visual:** Bell curve with spike marked "3σ from mean"
3. **Threshold table:**
   | Sensor Type | Low | High |
   |-------------|-----|------|
   | Temperature | 15°C | 35°C |
   | Humidity | 10% | 100% |
   | Pressure | 980 hPa | 1050 hPa |
4. **Alert log screenshot** (before suppression: 10 identical alerts; after: 1 alert + "5-min cooldown")

---

## PRODUCTION LESSON
Mention (casually, at the end):
> "In real systems, alert suppression is crucial. Without it, your ops team gets paged 50 times for the same problem. That's not intelligence — that's noise."

---

## TRANSITION TO NEXT SCRIPT
> "So we detect anomalies and generate alerts. But data science and dashboards are where the real insights come from. Let's look at what we can actually *see* in the system when we visualize it..."
