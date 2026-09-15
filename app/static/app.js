"use strict";

(function () {
  const statusEl = document.querySelector("#status");
  const productsBody = document.querySelector("#products-table tbody");
  const searchEl = document.querySelector("#filter-search");
  const categoryEl = document.querySelector("#filter-category");
  const applyBtn = document.querySelector("#filter-apply");
  const clearBtn = document.querySelector("#filter-clear");

  const formEl = document.querySelector("#product-form");
  const nameEl = document.querySelector("#name");
  const productCategoryEl = document.querySelector("#category");
  const volumeEl = document.querySelector("#volume_ml");
  const priceEl = document.querySelector("#price_cents");
  const stockEl = document.querySelector("#stock");
  const submitBtn = document.querySelector("#product-submit");

  const cancelBtn = document.createElement("button");
  cancelBtn.type = "button";
  cancelBtn.id = "product-cancel";
  cancelBtn.className = "secondary";
  cancelBtn.textContent = "Cancelar";
  cancelBtn.hidden = true;
  formEl.appendChild(cancelBtn);

  let currentParams = { category: "", search: "" };
  let editingId = null;

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

  function resetForm() {
    formEl.reset();
    editingId = null;
    submitBtn.textContent = "Guardar";
    cancelBtn.hidden = true;
  }

  function startEdit(product) {
    editingId = product.id;
    nameEl.value = product.name;
    productCategoryEl.value = product.category || "";
    volumeEl.value = product.volume_ml === null ? "" : product.volume_ml;
    priceEl.value = product.price_cents === null ? "" : product.price_cents;
    stockEl.value = product.stock;
    submitBtn.textContent = "Actualizar";
    cancelBtn.hidden = false;
    setStatus("Editando producto #" + product.id);
  }

  function renderProducts(products) {
    productsBody.textContent = "";
    if (!products.length) {
      productsBody.innerHTML = '<tr><td colspan="6">No hay productos</td></tr>';
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

      const actions = document.createElement("td");
      const editBtn = document.createElement("button");
      editBtn.type = "button";
      editBtn.className = "secondary";
      editBtn.textContent = "Editar";
      editBtn.addEventListener("click", function () {
        startEdit(product);
      });
      actions.appendChild(editBtn);

      row.append(name, category, volume, price, stock, actions);
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

  function validateForm() {
    if (!nameEl.value.trim()) {
      return "El nombre es obligatorio";
    }
    const numericFields = [
      ["volume_ml", volumeEl],
      ["price_cents", priceEl],
      ["stock", stockEl],
    ];
    for (let i = 0; i < numericFields.length; i++) {
      const field = numericFields[i][0];
      const input = numericFields[i][1];
      const value = input.value.trim();
      if (value !== "" && !/^\d+$/.test(value)) {
        return field + " debe ser un entero mayor o igual a 0";
      }
    }
    return "";
  }

  function buildPayload() {
    const payload = { name: nameEl.value.trim() };
    const categoryValue = productCategoryEl.value.trim();
    if (categoryValue) {
      payload.category = categoryValue;
    }
    const numericFields = [
      ["volume_ml", volumeEl],
      ["price_cents", priceEl],
      ["stock", stockEl],
    ];
    numericFields.forEach(function (cfg) {
      const field = cfg[0];
      const input = cfg[1];
      if (input.value.trim() !== "") {
        payload[field] = parseInt(input.value, 10);
      }
    });
    return payload;
  }

  function readApiError(body) {
    if (body && Array.isArray(body.detail)) {
      return body.detail
        .map(function (issue) {
          return issue.msg;
        })
        .join("; ");
    }
    if (body && typeof body.detail === "string") {
      return body.detail;
    }
    return "request failed";
  }

  formEl.addEventListener("submit", function (event) {
    event.preventDefault();
    const error = validateForm();
    if (error) {
      setStatus(error);
      return;
    }
    const url =
      editingId === null ? "/api/products" : "/api/products/" + editingId;
    const method = editingId === null ? "POST" : "PUT";
    fetch(url, {
      method: method,
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(buildPayload()),
    })
      .then(function (response) {
        if (response.ok) {
          resetForm();
          fetchProducts(currentParams);
          return;
        }
        return response.json().then(function (body) {
          throw new Error(readApiError(body));
        });
      })
      .catch(function (err) {
        setStatus(err.message || "request failed");
      });
  });

  cancelBtn.addEventListener("click", function () {
    resetForm();
    setStatus("Edición cancelada");
  });

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