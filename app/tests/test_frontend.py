import re
from typing import Any

from fastapi.testclient import TestClient

VODKA = {"name": "Vodka", "category": "Spirits", "volume_ml": 750, "price_cents": 15000, "stock": 10}
TEQUILA = {"name": "Tequila", "category": "Spirits", "volume_ml": 700, "price_cents": 21000, "stock": 5}
MALBEC = {"name": "Malbec", "category": "Wine", "volume_ml": 750, "price_cents": 8000, "stock": 3}


def create_product(client: TestClient, payload: dict[str, Any]) -> dict[str, Any]:
    response = client.post("/api/products", json=payload)
    assert response.status_code == 201
    return response.json()


def test_hash_routing_layout(client: TestClient):
    html = client.get("/").text
    assert "<header" in html
    assert "Liquor Management" in html
    assert 'href="#/dashboard"' in html
    assert 'href="#/products"' in html
    assert 'href="#/sales"' in html
    assert 'id="view-dashboard"' in html
    assert 'id="view-products"' in html
    assert 'id="view-sales"' in html


def test_dashboard_view_elements(client: TestClient):
    html = client.get("/").text
    assert 'id="view-dashboard"' in html
    assert 'id="dashboard-cards"' in html
    assert 'id="low-stock-table"' in html
    assert 'id="status"' in html


def test_products_view_elements(client: TestClient):
    html = client.get("/").text
    assert 'id="view-products"' in html
    assert 'id="filter-search"' in html
    assert 'id="filter-category"' in html
    assert 'id="filter-apply"' in html
    assert 'id="filter-clear"' in html
    assert 'id="products-table"' in html
    assert 'id="products-tbody"' in html
    assert 'id="product-form"' in html
    assert 'id="name"' in html
    assert 'id="category"' in html
    assert 'id="volume_ml"' in html
    assert 'id="price_cents"' in html
    assert 'id="stock"' in html
    assert 'id="product-submit"' in html


def test_sales_view_elements(client: TestClient):
    html = client.get("/").text
    assert 'id="view-sales"' in html
    assert 'id="sale-form"' in html
    assert 'id="sale-product"' in html
    assert 'id="sale-qty"' in html
    assert 'id="sales-table"' in html
    assert 'id="sales-table">\n            <thead' in html or '<thead' in html


def test_e2e_sales_flow_creates_product_registers_sale_updates_dashboard(client: TestClient):
    product = create_product(client, {**VODKA, "stock": 10})
    product_id = product["id"]

    sale_response = client.post("/api/sales", json={"product_id": product_id, "qty": 2})
    assert sale_response.status_code == 201
    sale = sale_response.json()
    assert sale["product_id"] == product_id
    assert sale["qty"] == 2
    assert sale["unit_price_cents"] == 15000
    assert sale["total_cents"] == 30000

    updated_product = client.get(f"/api/products/{product_id}").json()
    assert updated_product["stock"] == 8

    dashboard = client.get("/api/stats/dashboard").json()
    assert dashboard["total_products"] == 1
    assert dashboard["total_sales"] == 1
    assert dashboard["total_revenue_cents"] == 30000

    sales_list = client.get("/api/sales").json()
    assert len(sales_list) == 1
    assert sales_list[0]["id"] == sale["id"]
    assert sales_list[0]["qty"] == 2
    assert sales_list[0]["total_cents"] == 30000

    html = client.get("/").text
    assert 'id="sale-form"' in html
    assert 'id="sales-table"' in html


def test_e2e_products_crud_full_cycle(client: TestClient):
    created = create_product(client, VODKA)
    product_id = created["id"]

    listing = client.get("/api/products")
    assert listing.status_code == 200
    assert len(listing.json()) == 1
    assert listing.json()[0]["name"] == "Vodka"

    updated = client.put(f"/api/products/{product_id}", json={**VODKA, "name": "Vodka Premium", "price_cents": 18000})
    assert updated.status_code == 200
    body = updated.json()
    assert body["id"] == product_id
    assert body["name"] == "Vodka Premium"
    assert body["price_cents"] == 18000

    deleted = client.delete(f"/api/products/{product_id}")
    assert deleted.status_code == 204
    assert client.get(f"/api/products/{product_id}").status_code == 404

    html = client.get("/").text
    assert 'id="product-form"' in html
    assert 'id="products-table"' in html


def test_e2e_dashboard_low_stock_and_kpis(client: TestClient):
    create_product(client, {**VODKA, "stock": 10})
    create_product(client, {**TEQUILA, "stock": 5})
    create_product(client, {**MALBEC, "stock": 3})

    dashboard = client.get("/api/stats/dashboard").json()
    assert dashboard["total_products"] == 3
    assert dashboard["total_sales"] == 0
    assert dashboard["total_revenue_cents"] == 0

    low_stock = dashboard["low_stock"]
    assert [p["stock"] for p in low_stock] == [3, 5]
    assert [p["name"] for p in low_stock] == ["Malbec", "Tequila"]
    assert all(p["stock"] <= 5 for p in low_stock)

    html = client.get("/").text
    assert 'id="dashboard-cards"' in html
    assert 'id="low-stock-table"' in html


def test_e2e_products_filters_search_and_category(client: TestClient):
    create_product(client, VODKA)
    create_product(client, TEQUILA)
    create_product(client, MALBEC)

    by_category = client.get("/api/products", params={"category": "Spirits"})
    assert by_category.status_code == 200
    names = [p["name"] for p in by_category.json()]
    assert names == ["Vodka", "Tequila"]

    by_search = client.get("/api/products", params={"search": "malbec"})
    assert by_search.status_code == 200
    assert [p["name"] for p in by_search.json()] == ["Malbec"]

    combined = client.get("/api/products", params={"category": "Wine", "search": "malbec"})
    assert combined.status_code == 200
    assert [p["name"] for p in combined.json()] == ["Malbec"]

    empty_search = client.get("/api/products", params={"search": "nonexistent"})
    assert empty_search.status_code == 200
    assert empty_search.json() == []


def test_e2e_sale_updates_low_stock_on_dashboard(client: TestClient):
    product = create_product(client, {**VODKA, "stock": 5})
    product_id = product["id"]

    dashboard_before = client.get("/api/stats/dashboard").json()
    assert dashboard_before["total_products"] == 1
    assert any(p["stock"] == 5 for p in dashboard_before["low_stock"])

    client.post("/api/sales", json={"product_id": product_id, "qty": 2})

    dashboard_after = client.get("/api/stats/dashboard").json()
    assert dashboard_after["total_sales"] == 1
    assert dashboard_after["total_revenue_cents"] == 30000
    low_stock = dashboard_after["low_stock"]
    assert len(low_stock) == 1
    assert low_stock[0]["stock"] == 3
    assert low_stock[0]["name"] == "Vodka"


def test_root_serves_index_html(client: TestClient):
    response = client.get("/")
    assert response.status_code == 200
    assert response.headers["content-type"] == "text/html; charset=utf-8"
    html = response.text
    assert "<!DOCTYPE html>" in html
    assert 'id="products-table"' in html
    assert 'id="product-form"' in html
    assert 'id="filter-category"' in html
    assert 'id="filter-search"' in html
    assert 'id="status"' in html
    assert 'id="sale-form"' in html
    assert 'id="sales-table"' in html


def test_products_table_has_presentational_headers(client: TestClient):
    html = client.get("/").text
    table = re.search(r'<table id="products-table">(.*?)</table>', html, re.DOTALL)
    assert table is not None
    headers = {re.sub(r"\s+", " ", h).strip().lower() for h in re.findall(r"<th>(.*?)</th>", table.group(1))}
    assert headers == {"name", "category", "volume ml", "price", "stock"}


def test_sales_table_has_presentational_headers(client: TestClient):
    html = client.get("/").text
    table = re.search(r'<table id="sales-table">(.*?)</table>', html, re.DOTALL)
    assert table is not None
    headers = {re.sub(r"\s+", " ", h).strip().lower() for h in re.findall(r"<th>(.*?)</th>", table.group(1))}
    assert headers == {"id", "producto", "cantidad", "precio unit. ($)", "total ($)", "fecha"}


def test_products_view_has_elements(client: TestClient):
    html = client.get("/").text
    assert 'id="view-products"' in html
    assert 'id="filter-search"' in html
    assert 'id="filter-category"' in html
    assert 'id="filter-apply"' in html
    assert 'id="filter-clear"' in html
    assert 'id="products-table"' in html
    assert 'id="products-tbody"' in html
    assert 'id="product-form"' in html
    assert 'id="name"' in html
    assert 'id="category"' in html
    assert 'id="volume_ml"' in html
    assert 'id="price_cents"' in html
    assert 'id="stock"' in html
    assert 'id="product-submit"' in html


def test_sales_view_has_elements(client: TestClient):
    html = client.get("/").text
    assert 'id="view-sales"' in html
    assert 'id="sale-form"' in html
    assert 'id="sale-product"' in html
    assert 'id="sale-qty"' in html
    assert 'id="sales-table"' in html
    assert 'id="sales-table" tbody' in html or 'id="sales-table">\n            <thead' in html


def test_multi_page_layout_present(client: TestClient):
    html = client.get("/").text
    assert "<header" in html
    assert "Liquor Management" in html
    assert 'href="#/dashboard"' in html
    assert 'href="#/products"' in html
    assert 'href="#/sales"' in html
    assert 'id="view-dashboard"' in html
    assert 'id="view-products"' in html
    assert 'id="view-sales"' in html
    assert 'id="dashboard-cards"' in html
    assert 'id="low-stock-table"' in html


def test_low_stock_table_has_headers(client: TestClient):
    html = client.get("/").text
    table = re.search(r'<table id="low-stock-table">(.*?)</table>', html, re.DOTALL)
    assert table is not None
    headers = {re.sub(r"\s+", " ", h).strip().lower() for h in re.findall(r"<th>(.*?)</th>", table.group(1))}
    assert headers == {"producto", "stock"}


def test_static_style_css(client: TestClient):
    response = client.get("/static/style.css")
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/css")


def test_static_app_js(client: TestClient):
    response = client.get("/static/app.js")
    assert response.status_code == 200


def test_full_roundtrip_create_list_edit_delete(client: TestClient):
    created = create_product(client, VODKA)
    product_id = created["id"]

    listing = client.get("/api/products")
    assert listing.status_code == 200
    assert [p["name"] for p in listing.json()] == ["Vodka"]

    updated = client.put(f"/api/products/{product_id}", json={**VODKA, "name": "Vodka Premium", "price_cents": 18000})
    assert updated.status_code == 200
    body = updated.json()
    assert body["id"] == product_id
    assert body["name"] == "Vodka Premium"
    assert body["price_cents"] == 18000

    deleted = client.delete(f"/api/products/{product_id}")
    assert deleted.status_code == 204
    assert client.get(f"/api/products/{product_id}").status_code == 404


def test_filters_category_and_search(client: TestClient):
    create_product(client, VODKA)
    create_product(client, TEQUILA)
    create_product(client, MALBEC)

    by_category = client.get("/api/products", params={"category": "Spirits"})
    assert by_category.status_code == 200
    assert [p["name"] for p in by_category.json()] == ["Vodka", "Tequila"]

    by_search = client.get("/api/products", params={"search": "ma"})
    assert by_search.status_code == 200
    assert [p["name"] for p in by_search.json()] == ["Malbec"]

    combined = client.get("/api/products", params={"category": "Wine", "search": "ma"})
    assert combined.status_code == 200
    assert [p["name"] for p in combined.json()] == ["Malbec"]


def test_invalid_post_returns_422(client: TestClient):
    response = client.post("/api/products", json={"name": "Sin Stock", "stock": -1})
    assert response.status_code == 422
    assert response.json()["detail"][0]["type"] == "greater_than_equal"


def test_health_and_api_still_work(client: TestClient):
    assert client.get("/health").json() == {"status": "ok"}
    assert client.get("/api/products").status_code == 200