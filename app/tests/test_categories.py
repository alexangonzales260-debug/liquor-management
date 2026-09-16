from typing import Any

from fastapi.testclient import TestClient

VODKA = {"name": "Vodka", "category": "Spirits", "volume_ml": 750, "price_cents": 15000, "stock": 10}
WHISKY = {"name": "Whisky", "category": "Spirits", "volume_ml": 700, "price_cents": 25000, "stock": 5}
MALBEC = {"name": "Malbec", "category": "Wine", "volume_ml": 750, "price_cents": 8000, "stock": 3}


def create_category(client: TestClient, payload: dict[str, Any]) -> dict[str, Any]:
    response = client.post("/api/categories", json=payload)
    assert response.status_code == 201
    return response.json()


def create_product(client: TestClient, payload: dict[str, Any]) -> dict[str, Any]:
    response = client.post("/api/products", json=payload)
    assert response.status_code == 201
    return response.json()


def test_list_categories_empty(client: TestClient):
    response = client.get("/api/categories")
    assert response.status_code == 200
    assert response.json() == []


def test_create_category(client: TestClient):
    response = client.post("/api/categories", json={"name": "Spirits", "description": "Aguardientes"})
    assert response.status_code == 201
    body = response.json()
    assert body["id"] is not None
    assert body["name"] == "Spirits"
    assert body["description"] == "Aguardientes"
    assert body["products_count"] == 0
    assert "created_at" in body


def test_create_category_duplicate_400(client: TestClient):
    create_category(client, {"name": "Spirits"})
    response = client.post("/api/categories", json={"name": "Spirits"})
    assert response.status_code == 400
    assert response.json()["detail"] == "Category already exists"


def test_create_category_duplicate_case_insensitive_400(client: TestClient):
    create_category(client, {"name": "Spirits"})
    response = client.post("/api/categories", json={"name": "spirits"})
    assert response.status_code == 400


def test_create_category_empty_name_422(client: TestClient):
    response = client.post("/api/categories", json={"name": ""})
    assert response.status_code == 422


def test_get_category_by_id(client: TestClient):
    category = create_category(client, {"name": "Spirits"})
    response = client.get(f"/api/categories/{category['id']}")
    assert response.status_code == 200
    assert response.json()["name"] == "Spirits"


def test_get_category_not_found_404(client: TestClient):
    response = client.get("/api/categories/9999")
    assert response.status_code == 404


def test_update_category(client: TestClient):
    category = create_category(client, {"name": "Spirits", "description": "Aguardientes"})
    response = client.put(
        f"/api/categories/{category['id']}",
        json={"name": "Aguardientes", "description": "Bebidas fuertes"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["name"] == "Aguardientes"
    assert body["description"] == "Bebidas fuertes"


def test_update_category_same_name_ok(client: TestClient):
    category = create_category(client, {"name": "Spirits"})
    response = client.put(f"/api/categories/{category['id']}", json={"name": "Spirits"})
    assert response.status_code == 200
    assert response.json()["name"] == "Spirits"


def test_update_category_duplicate_name_400(client: TestClient):
    category = create_category(client, {"name": "Spirits"})
    create_category(client, {"name": "Wine"})
    response = client.put(f"/api/categories/{category['id']}", json={"name": "Wine"})
    assert response.status_code == 400
    assert response.json()["detail"] == "Category already exists"


def test_update_category_not_found_404(client: TestClient):
    response = client.put("/api/categories/9999", json={"name": "Spirits"})
    assert response.status_code == 404


def test_update_category_cascades_to_products(client: TestClient):
    category = create_category(client, {"name": "Spirits"})
    create_product(client, VODKA)
    create_product(client, WHISKY)
    create_product(client, MALBEC)
    response = client.put(f"/api/categories/{category['id']}", json={"name": "Licores"})
    assert response.status_code == 200
    products = client.get("/api/products", params={"category": "Licores"}).json()
    assert [p["name"] for p in products] == ["Vodka", "Whisky"]
    assert client.get("/api/products", params={"category": "Spirits"}).json() == []


def test_delete_category(client: TestClient):
    category = create_category(client, {"name": "Spirits"})
    response = client.delete(f"/api/categories/{category['id']}")
    assert response.status_code == 204
    assert client.get(f"/api/categories/{category['id']}").status_code == 404


def test_delete_category_with_products_400(client: TestClient):
    category = create_category(client, {"name": "Spirits"})
    create_product(client, VODKA)
    response = client.delete(f"/api/categories/{category['id']}")
    assert response.status_code == 400
    assert response.json()["detail"] == "Cannot delete category with associated products"


def test_delete_category_not_found_404(client: TestClient):
    response = client.delete("/api/categories/9999")
    assert response.status_code == 404


def test_list_categories_ordered_by_name(client: TestClient):
    create_category(client, {"name": "Vermouth"})
    create_category(client, {"name": "Ron"})
    create_category(client, {"name": "Cerveza"})
    response = client.get("/api/categories")
    assert response.status_code == 200
    names = [category["name"] for category in response.json()]
    assert names == sorted(names)


def test_products_count_in_list(client: TestClient):
    create_category(client, {"name": "Spirits"})
    create_category(client, {"name": "Wine"})
    create_product(client, VODKA)
    create_product(client, WHISKY)
    create_product(client, MALBEC)
    response = client.get("/api/categories")
    assert response.status_code == 200
    counts = {category["name"]: category["products_count"] for category in response.json()}
    assert counts == {"Spirits": 2, "Wine": 1}