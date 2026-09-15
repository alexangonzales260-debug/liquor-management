"use strict";

(function () {
  const statusEl = document.querySelector("#status");
  const productsBody = document.querySelector("#products-table tbody");
  const searchEl = document.querySelector("#filter-search");
  const categoryEl = document.querySelector("#filter-category");
  const applyBtn = document.querySelector("#filter-apply");
  const clearBtn = document.querySelector("#filter-clear");

  let currentParams = { category: "", search: "" };

  function setStatus(message) {
    statusEl.textContent = message;
  }

  function formatPrice(priceCents) {
    return "$" + (priceCents / 100).toFixed(2);
  }

  function buildQueryString(params) {
    const searchParams = new URLSearchParams();
    if (params.category) {
      searchParams.set("category", params.category);
    }
    if (params.search) {
      searchParams.set("search", params.search);
    }
    const query = searchParams.toString();
    return query ? "?" + query : "";
  }

  function renderProducts(products) {
    productsBody.textContent = "";
    if (!products.length) {
      productsBody.innerHTML = '<tr><td colspan="5">No hay productos</td></tr>';
      return;
    }
    products.forEach(function (product) {
      const row = document.createElement("tr");

      const name = document.createElement("td");
      name.textContent = product.name;

      const category = document.createElement("td");
      category.textContent = product.category || "";

      const volume = document.createElement("td");
      volume.textContent = product.volume_ml + " ml";

      const price = document.createElement("td");
      price.textContent = formatPrice(product.price_cents);

      const stock = document.createElement("td");
      stock.textContent = product.stock;

      row.append(name, category, volume, price, stock);
      productsBody.appendChild(row);
    });
  }

  function fetchProducts(params) {
    setStatus("Cargando productos...");
    fetch("/api/products" + buildQueryString(params))
      .then(function (response) {
        if (!response.ok) {
          throw new Error("request failed");
        }
        return response.json();
      })
      .then(function (products) {
        currentParams = params;
        renderProducts(products);
        setStatus("");
      })
      .catch(function () {
        setStatus("request failed");
      });
  }

  function readFilters() {
    return {
      category: categoryEl.value.trim(),
      search: searchEl.value.trim(),
    };
  }

  applyBtn.addEventListener("click", function () {
    fetchProducts(readFilters());
  });

  clearBtn.addEventListener("click", function () {
    searchEl.value = "";
    categoryEl.value = "";
    fetchProducts({ category: "", search: "" });
  });

  fetchProducts(currentParams);
})();