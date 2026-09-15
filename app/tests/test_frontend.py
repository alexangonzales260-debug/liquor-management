from fastapi.testclient import TestClient


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


def test_index_table_headers(client: TestClient):
    html = client.get("/").text
    for header in ["name", "category", "volume_ml", "price", "stock"]:
        assert header in html


def test_static_style_css(client: TestClient):
    response = client.get("/static/style.css")
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/css")


def test_static_app_js(client: TestClient):
    response = client.get("/static/app.js")
    assert response.status_code == 200


def test_health_and_api_still_work(client: TestClient):
    assert client.get("/health").json() == {"status": "ok"}
    assert client.get("/api/products").status_code == 200