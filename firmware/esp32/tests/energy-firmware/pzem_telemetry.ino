/**
 * Smart Campus Digital Twin - Edge Node Firmware
 * Sub-group: I-1 (Device & Edge Systems)
 * Node Type: Energy Telemetry (Phase 1 Prototype)
 * Hardware: ESP32 NodeMCU + PZEM-004T V3.0
 */

#include <WiFi.h>
#include <PubSubClient.h>
#include <PZEM004Tv30.h>
#include <ArduinoJson.h>

// ==========================================
// CONFIGURATION
// ==========================================
const char *ssid = "Dialog 356";
const char *password = "123456789";

// MQTT Broker Settings (Kong/Mosquitto)
const char *mqtt_server = "192.168.1.100";
const int mqtt_port = 1883;
const char *mqtt_user = "esp32_edge_01";
const char *mqtt_pass = "secure_device_password";
const char *mqtt_topic = "campus/EF/EF101/energy";

// ==========================================
// HARDWARE SETUP (ESP32 Serial2)
// ==========================================
#define PZEM_RX_PIN 16
#define PZEM_TX_PIN 17
#define PZEM_SERIAL Serial2

PZEM004Tv30 pzem(PZEM_SERIAL, PZEM_RX_PIN, PZEM_TX_PIN);

WiFiClient espClient;
PubSubClient mqttClient(espClient);

// ==========================================
// NETWORK INITIALIZATION
// ==========================================
void setup_wifi()
{
    delay(10);
    Serial.println();
    Serial.print("Connecting to WiFi: ");
    Serial.println(ssid);

    WiFi.begin(ssid, password);

    while (WiFi.status() != WL_CONNECTED)
    {
        delay(500);
        Serial.print(".");
    }
    Serial.println("\nWiFi connected. IP address: ");
    Serial.println(WiFi.localIP());
}

void reconnect_mqtt()
{
    // Loop until we're reconnected
    while (!mqttClient.connected())
    {
        Serial.print("Attempting MQTT connection...");
        // Attempt to connect with credentials
        if (mqttClient.connect("ESP32_Energy_Node_1", mqtt_user, mqtt_pass))
        {
            Serial.println("connected");
        }
        else
        {
            Serial.print("failed, rc=");
            Serial.print(mqttClient.state());
            Serial.println(" try again in 5 seconds");
            delay(5000);
        }
    }
}

// ==========================================
// MAIN SETUP
// ==========================================
void setup()
{
    Serial.begin(115200);

    setup_wifi();
    mqttClient.setServer(mqtt_server, mqtt_port);

    Serial.println("System Boot: Edge Node Initialized.");
}

// ==========================================
// MAIN LOOP & DATA SERIALIZATION
// ==========================================
void loop()
{
    if (!mqttClient.connected())
    {
        reconnect_mqtt();
    }
    mqttClient.loop();

    // 1. Read Sensor Data
    float voltage = pzem.voltage();
    float current = pzem.current();
    float power = pzem.power();
    float pf = pzem.pf();

    // 2. Validate Reading
    if (isnan(voltage))
    {
        Serial.println("Error reading PZEM sensor. Check wiring.");
    }
    else
    {
        // 3. Serialize to JSON Contract
        StaticJsonDocument<512> doc;

        doc["sensor_id"] = "energy_node_DB_floor1_roomA";
        doc["building_id"] = "EF";
        doc["room_id"] = "EF101";
        doc["sensor_type"] = "energy_watts";

        JsonObject metrics = doc.createNestedObject("metrics");
        metrics["voltage_v"] = voltage;
        metrics["current_a"] = current;
        metrics["active_power_w"] = power;
        metrics["power_factor"] = pf;

        // Fallback timestamp (System uptime in ms if NTP isn't configured yet)
        doc["timestamp_ms"] = millis();

        char payloadBuffer[512];
        serializeJson(doc, payloadBuffer);

        // 4. Publish Payload
        Serial.print("Publishing telemetry: ");
        Serial.println(payloadBuffer);

        // Publish with QoS 1 to ensure delivery
        mqttClient.publish(mqtt_topic, payloadBuffer, true);
    }

    // Poll every 5 seconds
    delay(5000);
}