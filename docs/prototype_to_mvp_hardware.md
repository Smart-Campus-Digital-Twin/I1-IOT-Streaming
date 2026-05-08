# Hardware Roadmap: Prototype to Minimum Viable Product (MVP)

## 1. Overview and Gap Analysis
The current integration relies on an event-driven software backend fueled by an automated Python `Simulator`. To transition this cyber-physical system to a production-ready Minimum Viable Product (MVP), the physical hardware layer must close specific operational gaps regarding deployment safety, fault tolerance, and macro-level infrastructure tracking.

## 2. Safety Mandate: Split-Core CT Clamps
For the physical MVP deployment, the hardware installation protocol strictly mandates the use of **Split-Core (Open) Current Transformers**.
* **The Gap:** Standard closed-loop CT clamps require powering down the university grid to cut the main live lines and thread them through the magnetic core.
* **The Engineering Solution:** Split-Core clamps feature a hinged magnetic core that snaps around a live wire. This ensures a **Zero-Downtime Deployment Architecture**, drastically reducing installation risk and preventing disruption to ongoing university lectures and critical server infrastructure.

## 3. Edge Resilience (Fault Tolerance & LWT)
* **The Gap:** Relying solely on the backend Data & Intelligence (I-2) watchdog timer to detect broken sensors introduces latency into the 3D Digital Twin UI.
* **The Engineering Solution:** We are architecting an **MQTT Last Will and Testament (LWT)** protocol directly into the ESP32 firmware.
  * *Execution:* Upon establishing a TCP connection with the Mosquitto broker, the ESP32 registers a localized "death certificate" payload. 
  * *Result:* If the edge node suffers an ungraceful disconnection (power cut, router failure), the broker instantly broadcasts an `{"status": "OFFLINE"}` payload to the `campus/health/nodes` topic. This provides sub-second failure detection, allowing the UI to flag the affected room's telemetry as "stale."

## 4. Macro-Level Tracking (Power Leakage)
* **The Gap:** Micro-monitoring (room-level MCBs) cannot account for 100% of the power entering a university building.
* **The Engineering Solution:** Phase 2 of the MVP roadmap introduces Tier-2 sensors (3-Phase Modbus RS485 energy meters) clamped to the main building intake. By subtracting the sum of the Tier-1 room sensors from the Tier-2 main intake, the analytics engine can mathematically isolate unmonitored "Power Leakage" caused by degraded wiring, power theft, or inefficient common-area facilities.

## 5. Software Evolution Plan (Change Request: Generator Load Shedding)
* **The Initiative:** The edge hardware team proposes a formal Change Request (CR) to introduce Tier-3 Infrastructure sensors monitoring the campus Diesel Generators.
* **The Architecture:** When a physical edge node detects the transition from the National Grid to Backup Generator power, it will publish a `CRITICAL_STATE` payload. The downstream software layers will utilize this event to automatically shed non-essential HVAC loads across the campus, preventing generator overload and catastrophic tripping.