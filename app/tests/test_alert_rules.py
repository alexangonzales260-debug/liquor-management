from app.models.alert_rule import EventType


def create_alert_rule(client, payload=None):
    payload = payload or {
        "name": "Test Rule",
        "event_type": EventType.low_stock.value,
        "condition_json": {"stock_lt": 5},
    }
    response = client.post("/api/alerts/rules", json=payload)
    assert response.status_code == 201
    return response.json()


def test_list_alert_rules_empty(client):
    response = client.get("/api/alerts/rules")
    assert response.status_code == 200
    assert response.json() == []


def test_create_alert_rule(client):
    response = client.post(
        "/api/alerts/rules",
        json={
            "name": "Low Stock Alert",
            "event_type": EventType.low_stock.value,
            "condition_json": {"stock_lt": 10},
        },
    )
    assert response.status_code == 201
    body = response.json()
    assert body["id"] is not None
    assert body["name"] == "Low Stock Alert"
    assert body["event_type"] == EventType.low_stock.value
    assert body["condition_json"] == {"stock_lt": 10}
    assert body["is_active"] is True
    assert "created_at" in body
    assert "updated_at" in body


def test_create_alert_rule_duplicate_422(client):
    create_alert_rule(client)
    response = client.post(
        "/api/alerts/rules",
        json={
            "name": "Test Rule",
            "event_type": EventType.low_stock.value,
            "condition_json": {"stock_lt": 5},
        },
    )
    assert response.status_code == 422
    assert response.json()["detail"] == "Alert rule name already exists"


def test_create_alert_rule_duplicate_case_insensitive_422(client):
    create_alert_rule(client)
    response = client.post(
        "/api/alerts/rules",
        json={
            "name": "test rule",
            "event_type": EventType.low_stock.value,
            "condition_json": {"stock_lt": 5},
        },
    )
    assert response.status_code == 422


def test_create_alert_rule_empty_name_422(client):
    response = client.post(
        "/api/alerts/rules",
        json={
            "name": "",
            "event_type": EventType.low_stock.value,
            "condition_json": {"stock_lt": 5},
        },
    )
    assert response.status_code == 422


def test_create_alert_rule_invalid_event_type_422(client):
    response = client.post(
        "/api/alerts/rules",
        json={
            "name": "Invalid Rule",
            "event_type": "invalid_type",
            "condition_json": {"stock_lt": 5},
        },
    )
    assert response.status_code == 422


def test_get_alert_rule_by_id(client):
    rule = create_alert_rule(client)
    response = client.get(f"/api/alerts/rules/{rule['id']}")
    assert response.status_code == 200
    body = response.json()
    assert body["name"] == "Test Rule"
    assert body["event_type"] == EventType.low_stock.value
    assert body["condition_json"] == {"stock_lt": 5}


def test_get_alert_rule_not_found_404(client):
    response = client.get("/api/alerts/rules/9999")
    assert response.status_code == 404


def test_update_alert_rule(client):
    rule = create_alert_rule(client)
    response = client.put(
        f"/api/alerts/rules/{rule['id']}",
        json={"name": "Updated Rule", "condition_json": {"stock_lt": 15}, "is_active": False},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["name"] == "Updated Rule"
    assert body["condition_json"] == {"stock_lt": 15}
    assert body["is_active"] is False
    assert body["event_type"] == EventType.low_stock.value


def test_update_alert_rule_same_name_ok(client):
    rule = create_alert_rule(client)
    response = client.put(f"/api/alerts/rules/{rule['id']}", json={"name": "Test Rule"})
    assert response.status_code == 200
    assert response.json()["name"] == "Test Rule"


def test_update_alert_rule_duplicate_name_422(client):
    rule = create_alert_rule(client)
    create_alert_rule(client, {"name": "Other Rule", "event_type": EventType.low_stock.value, "condition_json": {}})
    response = client.put(f"/api/alerts/rules/{rule['id']}", json={"name": "Other Rule"})
    assert response.status_code == 422
    assert response.json()["detail"] == "Alert rule name already exists"


def test_update_alert_rule_not_found_404(client):
    response = client.put(
        "/api/alerts/rules/9999",
        json={"name": "Nadie"},
    )
    assert response.status_code == 404


def test_delete_alert_rule(client):
    rule = create_alert_rule(client)
    response = client.delete(f"/api/alerts/rules/{rule['id']}")
    assert response.status_code == 204
    assert client.get(f"/api/alerts/rules/{rule['id']}").status_code == 404


def test_delete_alert_rule_not_found_404(client):
    response = client.delete("/api/alerts/rules/9999")
    assert response.status_code == 404


def test_list_alert_rules_filter_event_type(client):
    create_alert_rule(client, {"name": "Low Stock Rule", "event_type": EventType.low_stock.value, "condition_json": {}})
    create_alert_rule(client, {"name": "PO Overdue Rule", "event_type": EventType.po_overdue.value, "condition_json": {}})
    response = client.get("/api/alerts/rules", params={"event_type": EventType.low_stock.value})
    assert response.status_code == 200
    names = [r["name"] for r in response.json()]
    assert names == ["Low Stock Rule"]


def test_list_alert_rules_filter_is_active(client):
    create_alert_rule(client, {"name": "Active Rule", "event_type": EventType.low_stock.value, "condition_json": {}})
    create_alert_rule(client, {"name": "Inactive Rule", "event_type": EventType.low_stock.value, "condition_json": {}, "is_active": False})
    response = client.get("/api/alerts/rules", params={"is_active": "true"})
    assert response.status_code == 200
    names = [r["name"] for r in response.json()]
    assert names == ["Active Rule"]
    response = client.get("/api/alerts/rules", params={"is_active": "false"})
    assert response.status_code == 200
    names = [r["name"] for r in response.json()]
    assert names == ["Inactive Rule"]


def test_list_alert_rules_sorted_by_name(client):
    create_alert_rule(client, {"name": "Zeta", "event_type": EventType.low_stock.value, "condition_json": {}})
    create_alert_rule(client, {"name": "Alfa", "event_type": EventType.low_stock.value, "condition_json": {}})
    response = client.get("/api/alerts/rules")
    assert response.status_code == 200
    names = [r["name"] for r in response.json()]
    assert names == ["Alfa", "Zeta"]