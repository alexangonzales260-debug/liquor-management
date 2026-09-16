from sqlmodel import Session

from app.models.purchase_order import PurchaseOrder


def create_supplier(client, payload=None):
    payload = payload or {"name": "Proveedor Uno", "contact_person": "Ana Pérez", "phone": "555-0100"}
    response = client.post("/api/suppliers", json=payload)
    assert response.status_code == 201
    return response.json()


def add_purchase_order(db_session: Session, supplier_id: int, product_id: int) -> int:
    order = PurchaseOrder(
        supplier_id=supplier_id,
        product_id=product_id,
        qty_ordered=10,
        qty_received=0,
        unit_cost_cents=1000,
        total_cost_cents=10000,
    )
    db_session.add(order)
    db_session.commit()
    db_session.refresh(order)
    return order.id  # type: ignore[return-value]


def test_list_suppliers_empty(client):
    response = client.get("/api/suppliers")
    assert response.status_code == 200
    assert response.json() == []


def test_create_supplier(client):
    response = client.post(
        "/api/suppliers",
        json={"name": "Comercial Norte", "contact_person": "Ana", "email": "ana@norte.com", "tax_id": "RFC-1"},
    )
    assert response.status_code == 201
    body = response.json()
    assert body["id"] is not None
    assert body["name"] == "Comercial Norte"
    assert body["contact_person"] == "Ana"
    assert body["email"] == "ana@norte.com"
    assert body["tax_id"] == "RFC-1"
    assert body["order_count"] == 0
    assert "created_at" in body


def test_create_supplier_duplicate_422(client):
    create_supplier(client)
    response = client.post("/api/suppliers", json={"name": "Proveedor Uno"})
    assert response.status_code == 422
    assert response.json()["detail"] == "Supplier name already exists"


def test_create_supplier_duplicate_case_insensitive_422(client):
    create_supplier(client)
    response = client.post("/api/suppliers", json={"name": "proveedor uno"})
    assert response.status_code == 422


def test_create_supplier_empty_name_422(client):
    response = client.post("/api/suppliers", json={"name": ""})
    assert response.status_code == 422


def test_get_supplier_by_id(client):
    supplier = create_supplier(client)
    response = client.get(f"/api/suppliers/{supplier['id']}")
    assert response.status_code == 200
    body = response.json()
    assert body["name"] == "Proveedor Uno"
    assert body["order_count"] == 0


def test_get_supplier_not_found_404(client):
    response = client.get("/api/suppliers/9999")
    assert response.status_code == 404


def test_update_supplier(client):
    supplier = create_supplier(client)
    response = client.put(
        f"/api/suppliers/{supplier['id']}",
        json={"name": "Proveedor Renombrado", "phone": "555-0199"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["name"] == "Proveedor Renombrado"
    assert body["phone"] == "555-0199"
    assert body["contact_person"] == "Ana Pérez"


def test_update_supplier_same_name_ok(client):
    supplier = create_supplier(client)
    response = client.put(f"/api/suppliers/{supplier['id']}", json={"name": "Proveedor Uno"})
    assert response.status_code == 200
    assert response.json()["name"] == "Proveedor Uno"


def test_update_supplier_duplicate_name_422(client):
    supplier = create_supplier(client)
    create_supplier(client, {"name": "Otro Proveedor"})
    response = client.put(f"/api/suppliers/{supplier['id']}", json={"name": "Otro Proveedor"})
    assert response.status_code == 422
    assert response.json()["detail"] == "Supplier name already exists"


def test_update_supplier_not_found_404(client):
    response = client.put("/api/suppliers/9999", json={"name": "Nadie"})
    assert response.status_code == 404


def test_delete_supplier(client):
    supplier = create_supplier(client)
    response = client.delete(f"/api/suppliers/{supplier['id']}")
    assert response.status_code == 204
    assert client.get(f"/api/suppliers/{supplier['id']}").status_code == 404


def test_delete_supplier_not_found_404(client):
    response = client.delete("/api/suppliers/9999")
    assert response.status_code == 404


def test_delete_supplier_with_orders_409(client, db_session: Session):
    supplier = create_supplier(client)
    product = client.post(
        "/api/products",
        json={"name": "Vodka", "category": "Spirits", "volume_ml": 750, "price_cents": 15000, "stock": 10},
    ).json()
    add_purchase_order(db_session, supplier["id"], product["id"])
    response = client.delete(f"/api/suppliers/{supplier['id']}")
    assert response.status_code == 409
    assert response.json()["detail"] == "Supplier has associated purchase orders"
    assert client.get(f"/api/suppliers/{supplier['id']}").status_code == 200


def test_list_suppliers_search_q(client):
    create_supplier(client, {"name": "Comercial Norte", "contact_person": "Ana"})
    create_supplier(client, {"name": "Distribuidora Sur", "contact_person": "Luis"})
    response = client.get("/api/suppliers", params={"q": "ana"})
    assert response.status_code == 200
    names = [s["name"] for s in response.json()]
    assert names == ["Comercial Norte"]


def test_list_suppliers_sorted_by_name(client):
    create_supplier(client, {"name": "Zeta"})
    create_supplier(client, {"name": "Alfa"})
    response = client.get("/api/suppliers")
    assert response.status_code == 200
    names = [s["name"] for s in response.json()]
    assert names == ["Alfa", "Zeta"]