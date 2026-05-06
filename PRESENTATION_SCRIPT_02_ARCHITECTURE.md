# 🏗️ PRESENTATION SCRIPT 2: ARCHITECTURE & DATA FLOW
**Duration:** 75 seconds | **Visual:** System diagram with colored layers

---

## MAIN SCRIPT (Read Aloud)

Now let's look at the architecture. This system is built on three foundational layers:

**Layer 1 — The Edge: Sensors and Simulation**
We have a simulator that generates synthetic sensor readings from 160 virtual sensors — each with realistic values like temperature, humidity, pressure, vibration, and occupancy. Why a simulator? It lets us test without physical hardware, and it generates repeatable, realistic data.

**Layer 2 — The Message Backbone: MQTT and Kafka**
Sensors publish to an MQTT broker — a lightweight publish/subscribe system perfect for IoT. An ingestion bridge subscribes to all sensor topics, validates the data, and forwards it to Apache Kafka. Why two systems? MQTT is designed for edge devices with unstable connections. Kafka is designed for reliable, distributed message processing. This architecture lets us decouple the edge from the platform.

**Layer 3 — The Intelligence: Storage, Analytics, and Alerts**
Kafka feeds two parallel pipelines:
- **Processor:** Writes all sensor readings to InfluxDB for time-series analytics and PostgreSQL for long-term history.
- **Analytics:** Runs two independent anomaly detectors — one using Z-score statistics, one using simple threshold rules — and publishes alerts back to PostgreSQL.

Finally, **Prometheus and Grafana** let us monitor the whole system and visualize sensor data in real time.

That's the entire pipeline. Now let's zoom in on how the data actually moves.

---

## SPEAKER NOTES

| Timing | What to Do | What to Say |
|--------|-----------|------------|
| **0:00–0:10** | Show architecture diagram with labeled layers | Introduce 3 layers concept. Emphasize that this is a "proven pattern" (edge → messaging → intelligence). |
| **0:10–0:22** | Zoom into Layer 1: Simulator and sensors | Explain why simulator is used (testing, repeatability). Mention 160 sensors and 5 types. Don't dive into code details. |
| **0:22–0:40** | Highlight Layer 2: MQTT → Kafka bridge with arrows | **Key insight:** "Decoupling is the design pattern here." Explain why MQTT for edge, why Kafka for backend. Mention validation. |
| **0:40–0:55** | Zoom into Layer 3: Kafka → Processor + Analytics split | Use color or animation to show the "fork" in the pipeline. Briefly name the databases: InfluxDB (time-series), PostgreSQL (history). Say "anomaly detection" but don't explain the algorithms yet. |
| **0:55–1:15** | Show full loop: data flowing through from sensor → Prometheus/Grafana | Mention monitoring and dashboards. Emphasize "real-time" again. |

---

## KEY ARCHITECTURE CONCEPTS TO HIGHLIGHT
- **Decoupling:** MQTT handles unreliable edge; Kafka handles reliable platform. They don't need to know about each other.
- **Dual Storage:** InfluxDB for fast time-series queries, PostgreSQL for alerts and metadata.
- **Parallel Processing:** Processor and Analytics both consume Kafka independently — they can fail/update without affecting each other.

---

## VISUAL AIDS
Required in slide:
1. **C4 Container diagram** with 5 containers:
   - Simulator (actor)
   - Mosquitto (MQTT broker)
   - Kafka (message broker)
   - Processor (batch writer)
   - Analytics (anomaly detector)
   - Database icons (InfluxDB, PostgreSQL, Redis)
   - Prometheus + Grafana (monitoring)

2. **Color-coded layers:**
   - 🟦 Blue: Edge (Simulator, MQTT)
   - 🟪 Purple: Messaging (Kafka)
   - 🟩 Green: Intelligence (Analytics, Storage)

3. **Flow arrows** showing message direction and topic names:
   - `campus/*` (MQTT)
   - `sensors.*` (Kafka)
   - `alerts.*` (Kafka)

---

## TRANSITION TO NEXT SCRIPT
> "The architecture works because of a carefully designed data model. Let me show you the core abstraction that everything hinges on: the **SensorReading**. This single object connects the entire system..."
