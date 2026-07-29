"""
IoT Sensor Data Simulator
--------------------------
A lightweight Flask service that simulates readings from IoT sensors
(temperature, humidity, pressure) and exposes them via REST endpoints.
Optionally publishes each reading to an MQTT broker.
"""

import os
import random
import time
import threading
from datetime import datetime, timezone

from flask import Flask, jsonify

app = Flask(__name__)

# ---- Config (overridable via environment variables) ----
MQTT_ENABLED = os.getenv("MQTT_ENABLED", "false").lower() == "true"
MQTT_BROKER = os.getenv("MQTT_BROKER", "localhost")
MQTT_PORT = int(os.getenv("MQTT_PORT", "1883"))
MQTT_TOPIC = os.getenv("MQTT_TOPIC", "iot/sensors")
PUBLISH_INTERVAL = int(os.getenv("PUBLISH_INTERVAL", "5"))

# ---- In-memory "latest reading" store ----
latest_reading = {}
lock = threading.Lock()


def generate_reading():
    """Simulate a single sensor reading."""
    return {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "temperature_c": round(random.uniform(18.0, 32.0), 2),
        "humidity_pct": round(random.uniform(30.0, 70.0), 2),
        "pressure_hpa": round(random.uniform(990.0, 1025.0), 2),
        "device_id": os.getenv("DEVICE_ID", "sensor-sim-01"),
    }


def mqtt_publish_loop():
    """Background thread: periodically publish readings to MQTT, if enabled."""
    import json

    try:
        import paho.mqtt.client as mqtt
    except ImportError:
        print("paho-mqtt not installed; MQTT publishing disabled.")
        return

    client = mqtt.Client()
    try:
        client.connect(MQTT_BROKER, MQTT_PORT, keepalive=30)
    except Exception as exc:
        print(f"Could not connect to MQTT broker: {exc}")
        return

    client.loop_start()
    while True:
        with lock:
            reading = latest_reading.copy()
        if reading:
            client.publish(MQTT_TOPIC, json.dumps(reading))
        time.sleep(PUBLISH_INTERVAL)


def reading_update_loop():
    """Background thread: keep generating fresh readings."""
    global latest_reading
    while True:
        with lock:
            latest_reading = generate_reading()
        time.sleep(PUBLISH_INTERVAL)


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"}), 200


@app.route("/data", methods=["GET"])
def get_data():
    with lock:
        if not latest_reading:
            return jsonify(generate_reading()), 200
        return jsonify(latest_reading), 200


@app.route("/metrics", methods=["GET"])
def metrics():
    """Prometheus-style plaintext metrics (simple, hand-rolled)."""
    with lock:
        reading = latest_reading or generate_reading()

    lines = [
        "# HELP sensor_temperature_celsius Simulated temperature reading",
        "# TYPE sensor_temperature_celsius gauge",
        f'sensor_temperature_celsius{{device="{reading["device_id"]}"}} {reading["temperature_c"]}',
        "# HELP sensor_humidity_percent Simulated humidity reading",
        "# TYPE sensor_humidity_percent gauge",
        f'sensor_humidity_percent{{device="{reading["device_id"]}"}} {reading["humidity_pct"]}',
        "# HELP sensor_pressure_hpa Simulated pressure reading",
        "# TYPE sensor_pressure_hpa gauge",
        f'sensor_pressure_hpa{{device="{reading["device_id"]}"}} {reading["pressure_hpa"]}',
    ]
    return "\n".join(lines) + "\n", 200, {"Content-Type": "text/plain"}


def start_background_threads():
    threading.Thread(target=reading_update_loop, daemon=True).start()
    if MQTT_ENABLED:
        threading.Thread(target=mqtt_publish_loop, daemon=True).start()


# Start background threads when the module is imported (works under gunicorn too)
start_background_threads()

if __name__ == "__main__":
    port = int(os.getenv("PORT", "5000"))
    app.run(host="0.0.0.0", port=port)
