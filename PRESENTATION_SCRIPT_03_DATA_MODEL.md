# 📊 PRESENTATION SCRIPT 3: THE SENSOR READING & DATA MODEL
**Duration:** 75 seconds | **Visual:** JSON example and object diagram

---

## MAIN SCRIPT (Read Aloud)

Everything in this system flows through one core data structure: the **SensorReading**.

Here's what a SensorReading looks like:

```json
{
  "sensor_id": "building-a-f1-r01-temp",
  "building_id": "building-a",
  "floor": 1,
  "room_id": "building-a-f1-r01",
  "sensor_type": "temperature",
  "value": 22.3,
  "unit": "celsius",
  "timestamp_ms": 1714980240000,
  "quality": 1.0
}
```

This is not just any object — it's a **contract**. Every sensor, every service, every downstream consumer knows this shape. The simulator creates it. The bridge validates it. The processor stores it. The analytics engine reads it.

Why is this important? Because **one well-designed data model eliminates confusion**. There's no ambiguity about what building_id means, or whether the timestamp is in seconds or milliseconds. It's locked down from the start.

Now, each sensor publishes every 5 seconds. That's 160 sensors × 12 readings per minute = **1,920 readings per minute** flowing through this system. 

Notice the quality field? That's a quality score — it lets us track if a sensor is degrading or if data is partial. This is a real production concern that simulators often skip, but we didn't.

---

## SPEAKER NOTES

| Timing | What to Do | What to Say |
|--------|-----------|------------|
| **0:00–0:15** | Display the JSON example on-screen | Walk through each field slowly. Pause after `timestamp_ms` — this is often a source of bugs. Emphasize it's milliseconds. |
| **0:15–0:30** | Point to "contract" — maybe circle it or highlight it | Explain that contracts matter. Everyone agrees on the shape. No surprises downstream. Mention schema validation. |
| **0:30–0:45** | Show the math: 160 sensors × 12 readings/min | Let audience process the scale. **"1,920 readings per minute — that's 33 per second."** Emphasize: this is high-volume data. Not a file transfer. A stream. |
| **0:45–1:15** | Point to the `quality` field | Explain why quality matters. Give an example: "What if a sensor battery is dying? What if humidity sensor is stuck at 45%?" Quality flag helps us flag these. Shows engineering maturity. |

---

## RELATED ARCHITECTURES (From Graph Analysis)
The graph shows that `SensorReading` has **15 edges** — the most connected node in the system. It's used by:
- Simulator (creates it)
- Bridge (validates it)
- Processor (stores it)
- Analytics detectors (reads it for anomaly detection)
- AlertEvent (references it when an alert is triggered)

This validates that the data model is at the **heart of the system**.

---

## VISUAL AIDS
1. **JSON block** with syntax highlighting
2. **Field legend** below JSON:
   - `sensor_id` = globally unique identifier (includes building, floor, room, type)
   - `timestamp_ms` = **milliseconds since epoch** (UTC)
   - `quality` = 0.0–1.0 (1.0 = perfect, <0.9 = degraded)
   - `value` + `unit` = reading + physical unit
3. **Throughput meter:** 160 sensors → 1,920 readings/min → 33/sec
4. **Database icon** showing SensorReading flowing into InfluxDB and PostgreSQL

---

## COMMON PRESENTATION GOTCHAS
- **Don't spend 2 minutes on the JSON.** It's an example, not the code. Glance over it.
- **Don't read every field name.** Pick the 3 most important: `sensor_id`, `value`, `timestamp_ms`.
- **Don't explain Pydantic.** The data model is language-agnostic. It's a **contract**, not a Python class.

---

## TRANSITION TO NEXT SCRIPT
> "Now that we understand what sensor data looks like, here's the million-dollar question: **What do we do with 1,920 readings per minute?** We don't just store them. We analyze them in real-time for anomalies. Here's how..."
