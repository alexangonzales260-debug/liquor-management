from typing import Any

from fastapi.testclient import TestClient

VODKA = {"name": "Vodka", "category": "Spirits", "volume_ml": 750, "price_cents": 15000, "stock": 10}


def create_product(client: TestClient, payload: dict[str, Any]) -> dict[str, Any]:
    response = client.post("/api/products", json=payload)
    assert response.status_code == 201
    return response.json()


def test_list_restocks_empty(client: TestClient):
    response = client.get("/api/restocks")
    assert response.status_code == 200
    assert response.json() == []


def test_register_restock_increments_stock(client: TestClient):
    product = create_product(client, VODKA)
    response = client.post(
        "/api/restocks",
        json={
            "product_id": product["id"],
            "qty": 5,
            "unit_cost_cents": 12000,
            "notes": "Reabastecimiento",
        },
    )
    assert response.status_code == 201
    body = response.json()
    assert body["product_id"] == product["id"]
    assert body["qty"] == 5
    assert body["unit_cost_cents"] == 12000
    assert body["total_cost_cents"] == 60000
    assert body["notes"] == "Reabastecimiento"

    updated = client.get(f"/api/products/{product['id']}").json()
    assert updated["stock"] == 15


def test_register_restock_without_cost_or_notes(client: TestClient):
    product = create_product(client, VODKA)
    response = client.post(
        "/api/restocks", json={"product_id": product["id"], "qty": 3}
    )
    assert response.status_code == 201
    body = response.json()
    assert body["qty"] == 3
    assert body["unit_cost_cents"] is None
    assert body["total_cost_cents"] is None
    assert body["notes"] is None

    updated = client.get(f"/api/products/{product['id']}").json()
    assert updated["stock"] == 13


def test_restock_product_not_found_404(client: TestClient):
    response = client.post("/api/restocks", json={"product_id": 9999, "qty": 1})
    assert response.status_code == 404
    assert response.json()["detail"] == "Product not found"


def test_restock_qty_zero_422(client: TestClient):
    product = create_product(client, VODKA)
    response = client.post("/api/restocks", json={"product_id": product["id"], "qty": 0})
    assert response.status_code == 422


def test_list_restocks_ordered_desc(client: TestClient):
    product = create_product(client, VODKA)
    client.post("/api/restocks", json={"product_id": product["id"], "qty": 1})
    client.post("/api/restocks", json={"product_id": product["id"], "qty": 2})
    response = client.get("/api/restocks")
    assert response.status_code == 200
    restocks = response.json()
    assert len(restocks) == 2
    assert [r["qty"] for r in restocks] == [2, 1]