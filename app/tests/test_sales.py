from typing import Any

from fastapi.testclient import TestClient

VODKA = {"name": "Vodka", "category": "Spirits", "volume_ml": 750, "price_cents": 15000, "stock": 10}


def create_product(client: TestClient, payload: dict[str, Any]) -> dict[str, Any]:
    response = client.post("/api/products", json=payload)
    assert response.status_code == 201
    return response.json()


def test_register_sale_decrements_stock(client: TestClient):
    product = create_product(client, VODKA)
    response = client.post("/api/sales", json={"product_id": product["id"], "qty": 4})
    assert response.status_code == 201
    body = response.json()
    assert body["product_id"] == product["id"]
    assert body["qty"] == 4
    assert body["unit_price_cents"] == 15000
    assert body["total_cents"] == 60000

    updated = client.get(f"/api/products/{product['id']}").json()
    assert updated["stock"] == 6


def test_sale_product_not_found_404(client: TestClient):
    response = client.post("/api/sales", json={"product_id": 9999, "qty": 1})
    assert response.status_code == 404


def test_sale_over_stock_400(client: TestClient):
    product = create_product(client, VODKA)
    response = client.post("/api/sales", json={"product_id": product["id"], "qty": 11})
    assert response.status_code == 400


def test_sale_qty_zero_422(client: TestClient):
    product = create_product(client, VODKA)
    response = client.post("/api/sales", json={"product_id": product["id"], "qty": 0})
    assert response.status_code == 422


def test_sale_qty_negative_422(client: TestClient):
    product = create_product(client, VODKA)
    response = client.post("/api/sales", json={"product_id": product["id"], "qty": -3})
    assert response.status_code == 422