# IoT Sensor Simulator — CI/CD to Docker Hub

A lightweight Flask service that simulates IoT sensor readings (temperature,
humidity, pressure), exposes them over REST, publishes them to MQTT, and is
built/tested/pushed to Docker Hub automatically via GitHub Actions.

## Why this project

Bridges an IoT/cybersecurity background with a DevOps skill set: containerization,
CI/CD, vulnerability scanning, and (optionally) MQTT-based messaging — a common
pattern in real IoT platforms.

## Endpoints

| Route      | Description                                      |
|------------|---------------------------------------------------|
| `/health`  | Liveness check, returns `{"status": "ok"}`         |
| `/data`    | Latest simulated sensor reading (JSON)             |
| `/metrics` | Same reading in Prometheus plaintext exposition format |

## Run locally (no Docker)

```bash
cd app
pip install -r requirements.txt
python app.py
# visit http://localhost:5000/data
```

## Run with Docker

```bash
docker build -t iot-cicd-demo .
docker run -p 5000:5000 iot-cicd-demo
```

## Run with Docker Compose (app + MQTT broker)

```bash
docker-compose up --build
```

This starts the app plus an `eclipse-mosquitto` broker, with the app
publishing each reading to topic `iot/sensors` every `PUBLISH_INTERVAL`
seconds.

## Run tests

```bash
pip install -r app/requirements.txt pytest
pytest tests/ -v
```

## CI/CD Pipeline

Defined in `.github/workflows/docker-publish.yml`:

1. **On every push/PR to `main`**: install deps, lint (`flake8`), run `pytest`.
2. **On push to `main` only**: build the Docker image, scan it with **Trivy**
   for CRITICAL/HIGH CVEs, then push to Docker Hub tagged both `latest` and
   the commit SHA.

### Required GitHub secrets

| Secret                 | Value                                      |
|-------------------------|---------------------------------------------|
| `DOCKERHUB_USERNAME`    | Your Docker Hub username                    |
| `DOCKERHUB_TOKEN`       | A Docker Hub access token (not your password) |

Create the token at hub.docker.com → Account Settings → Security → New Access Token.

## Environment variables

| Variable            | Default            | Purpose                              |
|----------------------|---------------------|----------------------------------------|
| `MQTT_ENABLED`       | `false`             | Enable background MQTT publishing      |
| `MQTT_BROKER`        | `localhost`         | MQTT broker hostname                   |
| `MQTT_PORT`          | `1883`              | MQTT broker port                       |
| `MQTT_TOPIC`         | `iot/sensors`       | Topic to publish readings to           |
| `PUBLISH_INTERVAL`   | `5`                 | Seconds between simulated readings     |
| `DEVICE_ID`          | `sensor-sim-01`     | Identifier tagged onto each reading    |
| `PORT`               | `5000`              | Port Flask/Gunicorn binds to           |

## Possible next steps

- Add Prometheus + Grafana to `docker-compose.yml`, scrape `/metrics`
- Deploy to AWS ECS/EKS via Terraform, wired into this same pipeline
- Add Kubernetes manifests + Helm chart, deploy via ArgoCD (GitOps)
- Harden the Trivy step to hard-fail the pipeline on CRITICAL CVEs
