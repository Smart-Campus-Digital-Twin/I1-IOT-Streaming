#!/bin/bash

# ─────────────────────────────────────────────────────────────────────────────
#  Mosquitto Smoke Test
#
#  Verifies MQTT broker connectivity by publishing and subscribing to a test
#  message. Ensures the broker is operational and message delivery works.
#
#  Usage: bash scripts/smoke-test.sh
#  Exit codes: 0 = success, 1 = failure
# ─────────────────────────────────────────────────────────────────────────────

set -e

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$( cd "$SCRIPT_DIR/.." && pwd )"

# ── Configuration ───────────────────────────────────────────────────────────
BROKER_HOST="${MQTT_HOST:-localhost}"
BROKER_PORT="${MQTT_PORT:-1883}"
BROKER_USERNAME="${MQTT_USERNAME:-admin}"
BROKER_PASSWORD="${MQTT_PASSWORD:-password}"
TEST_TOPIC="campus/test/smoke"
TEST_PAYLOAD='{"timestamp":"2026-05-04T00:00:00Z","message":"smoke test","value":42}'
TIMEOUT=3
TMP_FILE="/tmp/mosquitto-smoke-test-$$.txt"

# ── Colors for output ───────────────────────────────────────────────────────
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# ── Cleanup on exit ─────────────────────────────────────────────────────────
cleanup() {
    rm -f "$TMP_FILE"
}
trap cleanup EXIT

echo -e "${YELLOW}[Mosquitto Smoke Test]${NC}"
echo "Broker: $BROKER_HOST:$BROKER_PORT"
echo "Topic: $TEST_TOPIC"
echo "Timeout: ${TIMEOUT}s"
echo ""

# ── Check if broker is reachable ────────────────────────────────────────────
echo -e "${YELLOW}[1/3]${NC} Checking broker connectivity..."
if ! timeout 5 mosquitto_sub -h "$BROKER_HOST" -p "$BROKER_PORT" \
    -u "$BROKER_USERNAME" -P "$BROKER_PASSWORD" \
    -t '$SYS/#' -C 1 -W 1 > /dev/null 2>&1; then
    echo -e "${RED}✗ FAILED${NC}: Broker unreachable at $BROKER_HOST:$BROKER_PORT"
    echo "Ensure Mosquitto is running:"
    echo "  docker-compose up -d mosquitto"
    exit 1
fi
echo -e "${GREEN}✓ PASSED${NC}: Broker is reachable"
echo ""

# ── Subscribe to test topic (with timeout) ──────────────────────────────────
echo -e "${YELLOW}[2/3]${NC} Subscribing to '$TEST_TOPIC' (${TIMEOUT}s timeout)..."
{
    timeout "$TIMEOUT" mosquitto_sub -h "$BROKER_HOST" -p "$BROKER_PORT" \
        -u "$BROKER_USERNAME" -P "$BROKER_PASSWORD" \
        -t "$TEST_TOPIC" -C 1 -W "${TIMEOUT}" > "$TMP_FILE" 2>&1 || true
} &
SUBSCRIBER_PID=$!

# Give subscriber time to connect
sleep 0.5

echo -e "${YELLOW}[3/3]${NC} Publishing test message..."
if mosquitto_pub -h "$BROKER_HOST" -p "$BROKER_PORT" \
    -u "$BROKER_USERNAME" -P "$BROKER_PASSWORD" \
    -t "$TEST_TOPIC" -m "$TEST_PAYLOAD" 2>&1; then
    echo -e "${GREEN}✓ PASSED${NC}: Message published"
else
    echo -e "${RED}✗ FAILED${NC}: Failed to publish message"
    exit 1
fi

# Wait for subscriber
wait $SUBSCRIBER_PID 2>/dev/null || true

# ── Verify message was received ─────────────────────────────────────────────
if [ -s "$TMP_FILE" ] && grep -q "$TEST_TOPIC" "$TMP_FILE" 2>/dev/null; then
    echo -e "${GREEN}✓ PASSED${NC}: Message received by subscriber"
    echo ""
    echo -e "${GREEN}=====================================${NC}"
    echo -e "${GREEN}All smoke tests PASSED${NC}"
    echo -e "${GREEN}=====================================${NC}"
    exit 0
else
    echo -e "${RED}✗ FAILED${NC}: Message was not received within ${TIMEOUT}s"
    echo "Received output:"
    cat "$TMP_FILE" 2>/dev/null || echo "(empty or error)"
    echo ""
    echo -e "${RED}=====================================${NC}"
    echo -e "${RED}Smoke test FAILED${NC}"
    echo -e "${RED}=====================================${NC}"
    exit 1
fi
