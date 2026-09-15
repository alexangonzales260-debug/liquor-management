from typing import Any

from fastapi.testclient import TestClient

VODKA = {"name": "Vodka", "category": "Spirits", "volume_ml": 750, "price_cents": 15000, "stock": 10}
TEQUILA = {"name": "Tequila", "category": "Spirits", "volume_ml": 700, "price_cents": 21000, "stock": 5}
MALBEC = {"name": "Malbec", "category": "Wine", "volume_ml": 750, "price_cents": 8000, "stock": 3}


def create_product(client: TestClient, payload: dict[str, Any]) -> dict[str, Any]:
    response = client.post("/api/products", json=payload)
    assert response.status_code == 201
    return response.json()


def test_create_product(client: TestClient):
    response = client.post("/api/products", json=VODKA)
    assert response.status_code == 201
    body = response.json()
    assert body["id"] is not None
    assert body["name"] == "Vodka"
    assert body["category"] == "Spirits"


def test_create_product_invalid_422(client: TestClient):
    response = client.post("/api/products", json={"name": "Sin Stock", "stock": -1})
    assert response.status_code == 422


def test_create_product_missing_name_422(client: TestClient):
    response = client.post("/api/products", json={"stock": 5})
    assert response.status_code == 422


def test_list_products(client: TestClient):
    create_product(client, VODKA)
    create_product(client, TEQUILA)
    response = client.get("/api/products")
    assert response.status_code == 200
    products = response.json()
    assert len(products) == 2


def test_list_products_empty(client: TestClient):
    response = client.get("/api/products")
    assert response.status_code == 200
    assert response.json() == []


def test_get_product_by_id(client: TestClient):
    product = create_product(client, VODKA)
    response = client.get(f"/api/products/{product['id']}")
    assert response.status_code == 200
    assert response.json()["name"] == "Vodka"


def test_get_product_not_found_404(client: TestClient):
    response = client.get("/api/products/9999")
    assert response.status_code == 404


def test_replace_product(client: TestClient):
    product = create_product(client, VODKA)
    updated = {**VODKA, "name": "Vodka Premium", "price_cents": 18000}
    response = client.put(f"/api/products/{product['id']}", json=updated)
    assert response.status_code == 200
    body = response.json()
    assert body["name"] == "Vodka Premium"
    assert body["price_cents"] == 18000


def test_replace_product_not_found_404(client: TestClient):
    response = client.put("/api/products/9999", json=VODKA)
    assert response.status_code == 404


def test_delete_product(client: TestClient):
    product = create_product(client, VODKA)
    response = client.delete(f"/api/products/{product['id']}")
    assert response.status_code == 204
    assert client.get(f"/api/products/{product['id']}").status_code == 404


def test_delete_product_not_found_404(client: TestClient):
    response = client.delete("/api/products/9999")
    assert response.status_code == 404


def test_filter_by_category_exact(client: TestClient):
    create_product(client, VODKA)
    create_product(client, TEQUILA)
    create_product(client, MALBEC)
    response = client.get("/api/products", params={"category": "Wine"})
    assert response.status_code == 200
    products = response.json()
    assert len(products) == 1
    assert products[0]["name"] == "Malbec"


def test_filter_by_category_no_match(client: TestClient):
    create_product(client, VODKA)
    response = client.get("/api/products", params={"category": "Beer"})
    assert response.status_code == 200
    assert response.json() == []


def test_search_case_insensitive(client: TestClient):
    create_product(client, VODKA)
    create_product(client, MALBEC)
    response = client.get("/api/products", params={"search": "malbec"})
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["name"] == "Malbec"


def test_search_uppercase(client: TestClient):
    create_product(client, VODKA)
    create_product(client, MALBEC)
    response = client.get("/api/products", params={"search": "VODKA"})
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["name"] == "Vodka"