import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "app"))

import app as flask_app  # noqa: E402


def get_client():
    flask_app.app.testing = True
    return flask_app.app.test_client()


def test_health():
    client = get_client()
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.get_json()["status"] == "ok"


def test_data_endpoint_returns_expected_fields():
    client = get_client()
    resp = client.get("/data")
    assert resp.status_code == 200
    body = resp.get_json()
    for field in ["timestamp", "temperature_c", "humidity_pct", "pressure_hpa", "device_id"]:
        assert field in body


def test_data_ranges_are_realistic():
    client = get_client()
    resp = client.get("/data")
    body = resp.get_json()
    assert 18.0 <= body["temperature_c"] <= 32.0
    assert 30.0 <= body["humidity_pct"] <= 70.0
    assert 990.0 <= body["pressure_hpa"] <= 1025.0


def test_metrics_endpoint_returns_prometheus_format():
    client = get_client()
    resp = client.get("/metrics")
    assert resp.status_code == 200
    text = resp.get_data(as_text=True)
    assert "sensor_temperature_celsius" in text
    assert "sensor_humidity_percent" in text
    assert "sensor_pressure_hpa" in text
