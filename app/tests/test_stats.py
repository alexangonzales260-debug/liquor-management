from typing import Any

from fastapi.testclient import TestClient

RUIN = {"name": "Ron", "category": "Spirits", "volume_ml": 750, "price_cents": 12000, "stock": 3}
WHISKY = {"name": "Whisky", "category": "Spirits", "volume_ml": 700, "price_cents": 25000, "stock": 5}
VODKA = {"name": "Vodka", "category": "Spirits", "volume_ml": 750, "price_cents": 15000, "stock": 10}


def create_product(client: TestClient, payload: dict[str, Any]) -> dict[str, Any]:
    response = client.post("/api/products", json=payload)
    assert response.status_code == 201
    return response.json()


def test_dashboard_initial_stats(client: TestClient):
    create_product(client, RUIN)
    create_product(client, WHISKY)
    create_product(client, VODKA)

    response = client.get("/api/stats/dashboard")
    assert response.status_code == 200
    body = response.json()
    assert body["total_products"] == 3
    assert body["total_sales"] == 0
    assert body["total_revenue_cents"] == 0
    low_stock = body["low_stock"]
    assert [p["id"] for p in low_stock] == sorted(p["id"] for p in low_stock)
    assert [p["stock"] for p in low_stock] == sorted(p["stock"] for p in low_stock)
    assert [p["stock"] for p in low_stock] == [3, 5]
    assert all(p["stock"] <= 5 for p in low_stock)
    assert VODKA["name"] not in [p["name"] for p in low_stock]


def test_dashboard_dashboard_empty(client: TestClient):
    response = client.get("/api/stats/dashboard")
    assert response.status_code == 200
    body = response.json()
    assert body == {
        "total_products": 0,
        "total_sales": 0,
        "total_revenue_cents": 0,
        "low_stock": [],
    }


def test_dashboard_after_sales(client: TestClient):
    vodka = create_product(client, VODKA)
    whisky = create_product(client, WHISKY)

    first = client.post("/api/sales", json={"product_id": vodka["id"], "qty": 2})
    assert first.status_code == 201
    second = client.post("/api/sales", json={"product_id": whisky["id"], "qty": 1})
    assert second.status_code == 201

    expected_revenue = first.json()["total_cents"] + second.json()["total_cents"]

    response = client.get("/api/stats/dashboard")
    assert response.status_code == 200
    body = response.json()
    assert body["total_products"] == 2
    assert body["total_sales"] == 2
    assert body["total_revenue_cents"] == expected_revenue

    low_stock = body["low_stock"]
    assert [p["stock"] for p in low_stock] == [4]
    assert low_stock[0]["name"] == WHISKY["name"]


def test_list_sales_desc_by_created_at(client: TestClient):
    vodka = create_product(client, VODKA)
    whisky = create_product(client, WHISKY)

    client.post("/api/sales", json={"product_id": vodka["id"], "qty": 1})
    client.post("/api/sales", json={"product_id": whisky["id"], "qty": 2})

    response = client.get("/api/sales")
    assert response.status_code == 200
    sales = response.json()
    assert len(sales) == 2
    assert sales[0]["id"] > sales[1]["id"]
    assert sales[0]["qty"] == 2
    assert sales[1]["qty"] == 1


def test_list_sales_desc_same_product(client: TestClient):
    vodka = create_product(client, VODKA)

    client.post("/api/sales", json={"product_id": vodka["id"], "qty": 1})
    client.post("/api/sales", json={"product_id": vodka["id"], "qty": 3})

    response = client.get("/api/sales")
    assert response.status_code == 200
    sales = response.json()
    assert len(sales) == 2
    assert sales[0]["id"] > sales[1]["id"]
    assert sales[0]["qty"] == 3
    assert sales[1]["qty"] == 1