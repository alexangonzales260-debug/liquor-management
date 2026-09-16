from datetime import date

PO_BASE = "/api/purchase-orders"


def _make_supplier(client, name="Proveedor PO"):
    response = client.post("/api/suppliers", json={"name": name})
    assert response.status_code == 201
    return response.json()


def _make_product(client, name="Licor PO", stock=0):
    response = client.post(
        "/api/products",
        json={"name": name, "category": "Spirits", "volume_ml": 750, "price_cents": 10000, "stock": stock},
    )
    assert response.status_code == 201
    return response.json()


def _create_po(client, supplier_id, product_id, qty_ordered=10, unit_cost_cents=1000, **extra):
    payload = {
        "supplier_id": supplier_id,
        "product_id": product_id,
        "qty_ordered": qty_ordered,
        "unit_cost_cents": unit_cost_cents,
    }
    payload.update(extra)
    response = client.post(PO_BASE, json=payload)
    assert response.status_code == 201
    return response.json()


def _receive(client, po_id, qty_received):
    return client.post(f"{PO_BASE}/{po_id}/receive", json={"qty_received": qty_received})


def test_list_purchase_orders_empty(client):
    response = client.get(PO_BASE)
    assert response.status_code == 200
    assert response.json() == []


def test_create_purchase_order_201(client):
    supplier = _make_supplier(client)
    product = _make_product(client)
    response = client.post(
        PO_BASE,
        json={
            "supplier_id": supplier["id"],
            "product_id": product["id"],
            "qty_ordered": 10,
            "unit_cost_cents": 1250,
            "expected_date": "2026-10-01",
            "notes": "Parada semanal",
        },
    )
    assert response.status_code == 201
    body = response.json()
    assert body["id"] is not None
    assert body["supplier_id"] == supplier["id"]
    assert body["supplier_name"] == "Proveedor PO"
    assert body["product_id"] == product["id"]
    assert body["product_name"] == "Licor PO"
    assert body["qty_ordered"] == 10
    assert body["qty_received"] == 0
    assert body["unit_cost_cents"] == 1250
    assert body["total_cost_cents"] == 12500
    assert body["status"] == "pending"
    assert body["order_date"] == date.today().isoformat()  # noqa: DTZ011
    assert body["expected_date"] == "2026-10-01"
    assert body["notes"] == "Parada semanal"
    assert body["received_date"] is None
    assert "created_at" in body


def test_create_purchase_order_invalid_supplier_404(client):
    product = _make_product(client)
    response = client.post(
        PO_BASE, json={"supplier_id": 9999, "product_id": product["id"], "qty_ordered": 5, "unit_cost_cents": 100}
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Supplier not found"


def test_create_purchase_order_invalid_product_404(client):
    supplier = _make_supplier(client)
    response = client.post(
        PO_BASE, json={"supplier_id": supplier["id"], "product_id": 9999, "qty_ordered": 5, "unit_cost_cents": 100}
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Product not found"


def test_get_purchase_order_200(client):
    supplier = _make_supplier(client)
    product = _make_product(client)
    po = _create_po(client, supplier["id"], product["id"])
    response = client.get(f"{PO_BASE}/{po['id']}")
    assert response.status_code == 200
    body = response.json()
    assert body["id"] == po["id"]
    assert body["supplier_name"] == "Proveedor PO"
    assert body["product_name"] == "Licor PO"


def test_get_purchase_order_404(client):
    response = client.get(f"{PO_BASE}/9999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Purchase order not found"


def test_update_purchase_order_200(client):
    supplier = _make_supplier(client, "Norte")
    other = _make_supplier(client, "Sur")
    product = _make_product(client)
    po = _create_po(client, supplier["id"], product["id"], qty_ordered=5, unit_cost_cents=1000)
    response = client.put(
        f"{PO_BASE}/{po['id']}",
        json={"supplier_id": other["id"], "qty_ordered": 10, "unit_cost_cents": 2000, "notes": "actualizado"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["supplier_id"] == other["id"]
    assert body["supplier_name"] == "Sur"
    assert body["qty_ordered"] == 10
    assert body["unit_cost_cents"] == 2000
    assert body["total_cost_cents"] == 20000
    assert body["notes"] == "actualizado"


def test_update_purchase_order_not_pending_409(client):
    supplier = _make_supplier(client)
    product = _make_product(client)
    po = _create_po(client, supplier["id"], product["id"])
    response = client.put(f"{PO_BASE}/{po['id']}", json={"status": "cancelled"})
    assert response.status_code == 200
    response = client.put(f"{PO_BASE}/{po['id']}", json={"notes": "nope"})
    assert response.status_code == 409
    assert response.json()["detail"] == "Only pending purchase orders can be updated"


def test_update_purchase_order_invalid_status_422(client):
    supplier = _make_supplier(client)
    product = _make_product(client)
    po = _create_po(client, supplier["id"], product["id"])
    response = client.put(f"{PO_BASE}/{po['id']}", json={"status": "en-route"})
    assert response.status_code == 422


def test_update_purchase_order_cannot_reduce_qty_received_400(client):
    supplier = _make_supplier(client)
    product = _make_product(client)
    po = _create_po(client, supplier["id"], product["id"], qty_ordered=10)
    response = client.put(f"{PO_BASE}/{po['id']}", json={"qty_received": 4})
    assert response.status_code == 200
    response = client.put(f"{PO_BASE}/{po['id']}", json={"qty_received": 2})
    assert response.status_code == 400
    assert response.json()["detail"] == "Cannot reduce qty_received"


def test_update_purchase_order_qty_ordered_below_qty_received_400(client):
    supplier = _make_supplier(client)
    product = _make_product(client)
    po = _create_po(client, supplier["id"], product["id"], qty_ordered=10)
    client.put(f"{PO_BASE}/{po['id']}", json={"qty_received": 4})
    response = client.put(f"{PO_BASE}/{po['id']}", json={"qty_ordered": 3})
    assert response.status_code == 400
    assert response.json()["detail"] == "qty_ordered cannot be below qty_received"


def test_update_purchase_order_not_found_404(client):
    response = client.put(f"{PO_BASE}/9999", json={"notes": "x"})
    assert response.status_code == 404


def test_delete_purchase_order_204(client):
    supplier = _make_supplier(client)
    product = _make_product(client)
    po = _create_po(client, supplier["id"], product["id"])
    response = client.delete(f"{PO_BASE}/{po['id']}")
    assert response.status_code == 204
    assert client.get(f"{PO_BASE}/{po['id']}").status_code == 404


def test_delete_purchase_order_not_found_404(client):
    response = client.delete(f"{PO_BASE}/9999")
    assert response.status_code == 404


def test_delete_purchase_order_received_409(client):
    supplier = _make_supplier(client)
    product = _make_product(client)
    po = _create_po(client, supplier["id"], product["id"], qty_ordered=5)
    _receive(client, po["id"], 5)
    response = client.delete(f"{PO_BASE}/{po['id']}")
    assert response.status_code == 409
    assert client.get(f"{PO_BASE}/{po['id']}").status_code == 200


def test_delete_purchase_order_partial_409(client):
    supplier = _make_supplier(client)
    product = _make_product(client)
    po = _create_po(client, supplier["id"], product["id"], qty_ordered=5)
    _receive(client, po["id"], 2)
    response = client.delete(f"{PO_BASE}/{po['id']}")
    assert response.status_code == 409
    assert client.get(f"{PO_BASE}/{po['id']}").status_code == 200


def test_receive_partial(client):
    supplier = _make_supplier(client)
    product = _make_product(client)
    po = _create_po(client, supplier["id"], product["id"], qty_ordered=10, unit_cost_cents=1000)
    response = _receive(client, po["id"], 4)
    assert response.status_code == 201
    body = response.json()
    assert body["po"]["status"] == "partial"
    assert body["po"]["qty_received"] == 4
    assert body["po"]["received_date"] is None
    assert body["restock_id"] is not None
    product_after = client.get(f"/api/products/{product['id']}").json()
    assert product_after["stock"] == 4
    restocks = client.get("/api/restocks").json()
    restock = next(r for r in restocks if r["id"] == body["restock_id"])
    assert restock["qty"] == 4
    assert restock["unit_cost_cents"] == 1000
    assert restock["total_cost_cents"] == 4000
    assert restock["purchase_order_id"] == po["id"]


def test_receive_complete(client):
    supplier = _make_supplier(client)
    product = _make_product(client)
    po = _create_po(client, supplier["id"], product["id"], qty_ordered=10, unit_cost_cents=1000)
    response = _receive(client, po["id"], 10)
    assert response.status_code == 201
    body = response.json()
    assert body["po"]["status"] == "received"
    assert body["po"]["qty_received"] == 10
    assert body["po"]["received_date"] == date.today().isoformat()  # noqa: DTZ011
    assert body["restock_id"] is not None
    product_after = client.get(f"/api/products/{product['id']}").json()
    assert product_after["stock"] == 10


def test_receive_partial_then_complete(client):
    supplier = _make_supplier(client)
    product = _make_product(client)
    po = _create_po(client, supplier["id"], product["id"], qty_ordered=10, unit_cost_cents=1000)
    first = _receive(client, po["id"], 6)
    second = _receive(client, po["id"], 4)
    assert first.json()["po"]["status"] == "partial"
    assert second.json()["po"]["status"] == "received"
    assert second.json()["restock_id"] != first.json()["restock_id"]
    product_after = client.get(f"/api/products/{product['id']}").json()
    assert product_after["stock"] == 10
    assert len(client.get("/api/restocks").json()) == 2


def test_receive_exceeds_pending_400(client):
    supplier = _make_supplier(client)
    product = _make_product(client)
    po = _create_po(client, supplier["id"], product["id"], qty_ordered=10)
    assert _receive(client, po["id"], 4).status_code == 201
    response = _receive(client, po["id"], 7)
    assert response.status_code == 400
    product_after = client.get(f"/api/products/{product['id']}").json()
    assert product_after["stock"] == 4


def test_receive_on_received_409(client):
    supplier = _make_supplier(client)
    product = _make_product(client)
    po = _create_po(client, supplier["id"], product["id"], qty_ordered=5)
    assert _receive(client, po["id"], 5).status_code == 201
    response = _receive(client, po["id"], 1)
    assert response.status_code == 409
    assert response.json()["detail"] == "Only pending or partial purchase orders can receive stock"


def test_receive_on_cancelled_409(client):
    supplier = _make_supplier(client)
    product = _make_product(client)
    po = _create_po(client, supplier["id"], product["id"], qty_ordered=5)
    client.put(f"{PO_BASE}/{po['id']}", json={"status": "cancelled"})
    response = _receive(client, po["id"], 1)
    assert response.status_code == 409


def test_receive_zero_qty_422(client):
    supplier = _make_supplier(client)
    product = _make_product(client)
    po = _create_po(client, supplier["id"], product["id"], qty_ordered=5)
    response = _receive(client, po["id"], 0)
    assert response.status_code == 422


def test_receive_not_found_404(client):
    response = _receive(client, 9999, 1)
    assert response.status_code == 404


def test_list_purchase_orders_order_desc(client):
    supplier = _make_supplier(client)
    product = _make_product(client)
    po1 = _create_po(client, supplier["id"], product["id"])
    po2 = _create_po(client, supplier["id"], product["id"])
    response = client.get(PO_BASE)
    assert response.status_code == 200
    ids = [po["id"] for po in response.json()]
    assert ids == [po2["id"], po1["id"]]


def test_list_purchase_orders_filters(client):
    supplier_a = _make_supplier(client, "Alfa")
    supplier_b = _make_supplier(client, "Beta")
    whisky = _make_product(client, "Whisky")
    ron = _make_product(client, "Ron")
    po_a = _create_po(client, supplier_a["id"], whisky["id"])
    po_b = _create_po(client, supplier_b["id"], ron["id"])
    client.put(f"{PO_BASE}/{po_b['id']}", json={"status": "cancelled"})

    by_supplier = client.get(PO_BASE, params={"supplier_id": supplier_a["id"]}).json()
    assert [po["id"] for po in by_supplier] == [po_a["id"]]

    by_product = client.get(PO_BASE, params={"product_id": ron["id"]}).json()
    assert [po["id"] for po in by_product] == [po_b["id"]]

    by_status = client.get(PO_BASE, params={"status": "cancelled"}).json()
    assert [po["id"] for po in by_status] == [po_b["id"]]

    by_supplier_name = client.get(PO_BASE, params={"q": "beta"}).json()
    assert [po["id"] for po in by_supplier_name] == [po_b["id"]]

    by_product_name = client.get(PO_BASE, params={"q": "whiskey"}).json()
    assert by_product_name == []