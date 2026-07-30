# IoT Sensor Simulator — CI/CD to Docker Hub

A lightweight Flask service that simulates IoT sensor readings (temperature,
humidity, pressure), exposes them over REST, publishes them to MQTT, and is
built/tested/pushed to Docker Hub automatically via GitHub Actions.


## Endpoints

| Route      | Description                                       |
|------------|---------------------------------------------------|
| `/health`  | Liveness check, returns `{"status": "ok"}`         |
| `/data`    | Latest simulated sensor reading (JSON)             |
| `/metrics` | Same reading in Prometheus plaintext exposition format |

## Environment variables

| Variable             | Default             | Purpose                              |
|----------------------|---------------------|----------------------------------------|
| `MQTT_ENABLED`       | `false`             | Enable background MQTT publishing      |
| `MQTT_BROKER`        | `localhost`         | MQTT broker hostname                   |
| `MQTT_PORT`          | `1883`              | MQTT broker port                       |
| `MQTT_TOPIC`         | `iot/sensors`       | Topic to publish readings to           |
| `PUBLISH_INTERVAL`   | `5`                 | Seconds between simulated readings     |
| `DEVICE_ID`          | `sensor-sim-01`     | Identifier tagged onto each reading    |
| `PORT`               | `5000`              | Port Flask/Gunicorn binds to           |
