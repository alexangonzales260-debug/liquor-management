"use strict";

(function () {
  const VIEWS = ["dashboard", "products", "sales", "categories"];
  const DEFAULT_VIEW = "dashboard";

  const statusEl = document.querySelector("#status");
  const cardsEl = document.querySelector("#dashboard-cards");
  const lowStockBody = document.querySelector("#low-stock-table tbody");
  const viewEls = Array.prototype.slice.call(
    document.querySelectorAll(".view"),
  );
  const navLinks = Array.prototype.slice.call(
    document.querySelectorAll(".sidebar a"),
  );
  const sidebarToggleEl = document.querySelector("#sidebar-toggle");

  const saleForm = document.querySelector("#sale-form");
  const saleProductSelect = document.querySelector("#sale-product");
  const saleQtyInput = document.querySelector("#sale-qty");
  const salesTableBody = document.querySelector("#sales-table tbody");

  const productForm = document.querySelector("#product-form");
  const productSubmitBtn = document.querySelector("#product-submit");
  const productsTbody = document.querySelector("#products-tbody");
  const filterSearch = document.querySelector("#filter-search");
  const filterCategory = document.querySelector("#filter-category");
  const filterApplyBtn = document.querySelector("#filter-apply");
  const filterClearBtn = document.querySelector("#filter-clear");

  const categoryForm = document.querySelector("#category-form");
  const categoryNameInput = document.querySelector("#category-name");
  const categoryDescInput = document.querySelector("#category-description");
  const categorySubmitBtn = document.querySelector("#category-submit");
  const categoryCancelBtn = document.querySelector("#category-cancel");
  const categoriesTbody = document.querySelector("#categories-tbody");

  let currentProductId = null;
  let productsCache = [];
  let currentCategoryId = null;
  let categoriesCache = [];

  function currentView() {
    const base = window.location.hash.replace(/^#\/?/, "").split("/")[0];
    return VIEWS.indexOf(base) !== -1 ? base : DEFAULT_VIEW;
  }

  function activateView(view) {
    viewEls.forEach(function (el) {
      el.classList.toggle("active", el.id === "view-" + view);
    });
    navLinks.forEach(function (link) {
      link.classList.toggle(
        "active",
        link.getAttribute("data-view") === view,
      );
    });
  }

  function setStatus(message, kind) {
    statusEl.textContent = message;
    statusEl.classList.remove("error", "loading");
    if (kind) {
      statusEl.classList.add(kind);
    }
  }

  function formatMoney(cents) {
    return "$" + (cents / 100).toFixed(2);
  }

  function formatDate(isoString) {
    const date = new Date(isoString);
    return date.toLocaleDateString("es-ES", {
      year: "numeric",
      month: "2-digit",
      day: "2-digit",
      hour: "2-digit",
      minute: "2-digit",
    });
  }

  function renderKpiCards(data) {
    cardsEl.textContent = "";
    const cards = [
      { label: "Productos", value: String(data.total_products) },
      { label: "Ventas", value: String(data.total_sales) },
      { label: "Ingresos", value: formatMoney(data.total_revenue_cents) },
    ];
    cards.forEach(function (card) {
      const el = document.createElement("div");
      el.className = "kpi-card";
      const label = document.createElement("span");
      label.className = "kpi-label";
      label.textContent = card.label;
      const value = document.createElement("span");
      value.className = "kpi-value";
      value.textContent = card.value;
      el.append(label, value);
      cardsEl.appendChild(el);
    });
  }

  function renderLowStock(rows) {
    lowStockBody.textContent = "";
    if (!rows.length) {
      lowStockBody.innerHTML =
        '<tr><td colspan="2" class="empty-row">Sin productos con stock bajo</td></tr>';
      return;
    }
    rows.forEach(function (row) {
      const tr = document.createElement("tr");
      const name = document.createElement("td");
      name.textContent = row.name;
      const stock = document.createElement("td");
      stock.textContent = row.stock;
      tr.append(name, stock);
      lowStockBody.appendChild(tr);
    });
  }

  function loadDashboard() {
    if (!statusEl || !cardsEl || !lowStockBody) {
      return;
    }
    setStatus("Cargando dashboard...", "loading");
    fetch("/api/stats/dashboard")
      .then(function (response) {
        if (!response.ok) {
          throw new Error("request failed");
        }
        return response.json();
      })
      .then(function (data) {
        renderKpiCards(data);
        renderLowStock(data.low_stock || []);
        setStatus("");
      })
      .catch(function () {
        setStatus("request failed", "error");
      });
  }

  function loadProductsForSaleSelect() {
    fetch("/api/products")
      .then(function (response) {
        if (!response.ok) throw new Error("Failed to load products");
        return response.json();
      })
      .then(function (products) {
        productsCache = products;
        saleProductSelect.innerHTML = '<option value="">Seleccionar producto...</option>';
        products.forEach(function (product) {
          const option = document.createElement("option");
          option.value = product.id;
          option.textContent = product.name + (product.category ? " (" + product.category + ")" : "") + " - Stock: " + product.stock;
          saleProductSelect.appendChild(option);
        });
      })
      .catch(function () {
        setStatus("Error al cargar productos", "error");
      });
  }

  function loadSales() {
    setStatus("Cargando ventas...", "loading");
    fetch("/api/sales")
      .then(function (response) {
        if (!response.ok) throw new Error("Failed to load sales");
        return response.json();
      })
      .then(function (sales) {
        salesTableBody.innerHTML = "";
        if (!sales.length) {
          salesTableBody.innerHTML =
            '<tr><td colspan="6" class="empty-row">Sin ventas registradas</td></tr>';
          setStatus("");
          return;
        }
        sales.forEach(function (sale) {
          const tr = document.createElement("tr");
          const product = productsCache.find(function (p) { return p.id === sale.product_id; });
          const productName = product ? product.name : "Desconocido";
          tr.innerHTML =
            "<td>" + sale.id + "</td>" +
            "<td>" + productName + "</td>" +
            "<td>" + sale.qty + "</td>" +
            "<td>" + formatMoney(sale.unit_price_cents) + "</td>" +
            "<td>" + formatMoney(sale.total_cents) + "</td>" +
            "<td>" + formatDate(sale.created_at) + "</td>";
          salesTableBody.appendChild(tr);
        });
        setStatus("");
      })
      .catch(function () {
        setStatus("Error al cargar ventas", "error");
      });
  }

  function handleSaleSubmit(event) {
    event.preventDefault();
    const productId = parseInt(saleProductSelect.value, 10);
    const qty = parseInt(saleQtyInput.value, 10);

    if (!productId || isNaN(qty) || qty < 1) {
      setStatus("Selecciona un producto y cantidad válida", "error");
      return;
    }

    setStatus("Registrando venta...", "loading");
    fetch("/api/sales", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ product_id: productId, qty: qty }),
    })
      .then(function (response) {
        if (!response.ok) {
          return response.json().then(function (data) {
            throw new Error(data.detail || "Error al registrar venta");
          });
        }
        return response.json();
      })
      .then(function () {
        setStatus("Venta registrada", "loading");
        saleForm.reset();
        loadProductsForSaleSelect();
        loadSales();
        loadDashboard();
      })
      .catch(function (error) {
        setStatus(error.message, "error");
      });
  }

  function loadProductsList() {
    const search = filterSearch.value.trim();
    const category = filterCategory.value.trim();
    const params = new URLSearchParams();
    if (search) params.append("search", search);
    if (category) params.append("category", category);

    setStatus("Cargando productos...", "loading");
    fetch("/api/products?" + params.toString())
      .then(function (response) {
        if (!response.ok) throw new Error("Failed to load products");
        return response.json();
      })
      .then(function (products) {
        productsCache = products;
        renderProductsTable(products);
        setStatus("");
      })
      .catch(function () {
        setStatus("Error al cargar productos", "error");
      });
  }

  function renderProductsTable(products) {
    productsTbody.innerHTML = "";
    if (!products.length) {
      productsTbody.innerHTML =
        '<tr><td colspan="6" class="empty-row">Sin productos</td></tr>';
      return;
    }
    products.forEach(function (product) {
      const tr = document.createElement("tr");
      tr.innerHTML =
        "<td>" + product.name + "</td>" +
        "<td>" + (product.category || "") + "</td>" +
        "<td>" + (product.volume_ml || "") + "</td>" +
        "<td>" + (product.price_cents !== null ? formatMoney(product.price_cents) : "") + "</td>" +
        "<td>" + product.stock + "</td>" +
        '<td class="actions">' +
          '<button type="button" class="edit-btn" data-id="' + product.id + '">Editar</button>' +
          '<button type="button" class="danger delete-btn" data-id="' + product.id + '">Borrar</button>' +
        "</td>";
      productsTbody.appendChild(tr);
    });
  }

  function clearProductForm() {
    productForm.reset();
    currentProductId = null;
    productSubmitBtn.textContent = "Guardar";
    productForm.querySelectorAll("input").forEach(function (input) {
      input.removeAttribute("disabled");
    });
  }

  function fillProductForm(product) {
    currentProductId = product.id;
    document.querySelector("#name").value = product.name;
    document.querySelector("#category").value = product.category || "";
    document.querySelector("#volume_ml").value = product.volume_ml || "";
    document.querySelector("#price_cents").value = product.price_cents !== null ? product.price_cents : "";
    document.querySelector("#stock").value = product.stock;
    productSubmitBtn.textContent = "Actualizar";
  }

  function handleProductSubmit(event) {
    event.preventDefault();
    const payload = {
      name: document.querySelector("#name").value.trim(),
      category: document.querySelector("#category").value.trim() || null,
      volume_ml: parseInt(document.querySelector("#volume_ml").value, 10) || null,
      price_cents: parseInt(document.querySelector("#price_cents").value, 10) || null,
      stock: parseInt(document.querySelector("#stock").value, 10) || 0,
    };

    if (!payload.name) {
      setStatus("El nombre es obligatorio", "error");
      return;
    }

    const url = currentProductId ? "/api/products/" + currentProductId : "/api/products";
    const method = currentProductId ? "PUT" : "POST";

    setStatus(currentProductId ? "Actualizando..." : "Guardando...", "loading");
    fetch(url, {
      method: method,
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    })
      .then(function (response) {
        if (!response.ok) {
          return response.json().then(function (data) {
            throw new Error(data.detail || "Error al guardar");
          });
        }
        return response.json();
      })
      .then(function () {
        setStatus(currentProductId ? "Producto actualizado" : "Producto creado", "loading");
        clearProductForm();
        loadProductsList();
        loadProductsForSaleSelect();
        loadDashboard();
      })
      .catch(function (error) {
        setStatus(error.message, "error");
      });
  }

  function handleProductAction(event) {
    const target = event.target;
    if (target.classList.contains("edit-btn")) {
      const productId = parseInt(target.getAttribute("data-id"), 10);
      const product = productsCache.find(function (p) { return p.id === productId; });
      if (product) fillProductForm(product);
    } else if (target.classList.contains("delete-btn")) {
      const productId = parseInt(target.getAttribute("data-id"), 10);
      if (!confirm("¿Eliminar este producto?")) return;
      setStatus("Eliminando...", "loading");
      fetch("/api/products/" + productId, { method: "DELETE" })
        .then(function (response) {
          if (!response.ok) {
            return response.json().then(function (data) {
              throw new Error(data.detail || "Error al eliminar");
            });
          }
          setStatus("Producto eliminado", "loading");
          loadProductsList();
          loadProductsForSaleSelect();
          loadDashboard();
        })
        .catch(function (error) {
          setStatus(error.message, "error");
        });
    }
  }

  function applyFilters() {
    loadProductsList();
  }

  function clearFilters() {
    filterSearch.value = "";
    filterCategory.value = "";
    loadProductsList();
  }

  function apiErrorDetail(data, fallback) {
    if (data && data.detail) {
      if (Array.isArray(data.detail)) {
        return data.detail.map(function (err) { return err.msg || err; }).join("; ");
      }
      return data.detail;
    }
    return fallback;
  }

  function loadCategories() {
    if (!statusEl || !categoriesTbody) {
      return;
    }
    setStatus("Cargando categorías...", "loading");
    fetch("/api/categories")
      .then(function (response) {
        if (!response.ok) throw new Error("Failed to load categories");
        return response.json();
      })
      .then(function (categories) {
        categoriesCache = categories;
        renderCategoriesTable(categories);
        setStatus("");
      })
      .catch(function () {
        setStatus("Error al cargar categorías", "error");
      });
  }

  function renderCategoriesTable(categories) {
    categoriesTbody.innerHTML = "";
    if (!categories.length) {
      categoriesTbody.innerHTML =
        '<tr><td colspan="5" class="empty-row">Sin categorías</td></tr>';
      return;
    }
    categories.forEach(function (category) {
      const tr = document.createElement("tr");
      tr.innerHTML =
        "<td>" + category.id + "</td>" +
        "<td>" + (category.name || "") + "</td>" +
        "<td>" + (category.description || "") + "</td>" +
        "<td>" + category.products_count + "</td>" +
        '<td class="actions">' +
          '<button type="button" class="edit-category-btn" data-id="' + category.id + '">Editar</button>' +
          '<button type="button" class="danger delete-category-btn" data-id="' + category.id + '">Borrar</button>' +
        "</td>";
      categoriesTbody.appendChild(tr);
    });
  }

  function clearCategoryForm() {
    categoryForm.reset();
    currentCategoryId = null;
    categorySubmitBtn.textContent = "Guardar";
    categoryCancelBtn.classList.add("hidden");
  }

  function fillCategoryForm(category) {
    currentCategoryId = category.id;
    categoryNameInput.value = category.name;
    categoryDescInput.value = category.description || "";
    categorySubmitBtn.textContent = "Actualizar";
    categoryCancelBtn.classList.remove("hidden");
  }

  function handleCategorySubmit(event) {
    event.preventDefault();
    const payload = {
      name: categoryNameInput.value.trim(),
      description: categoryDescInput.value.trim() || null,
    };

    if (!payload.name) {
      setStatus("El nombre es obligatorio", "error");
      return;
    }

    const url = currentCategoryId ? "/api/categories/" + currentCategoryId : "/api/categories";
    const method = currentCategoryId ? "PUT" : "POST";

    setStatus(currentCategoryId ? "Actualizando..." : "Guardando...", "loading");
    fetch(url, {
      method: method,
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    })
      .then(function (response) {
        if (!response.ok) {
          return response.json().then(function (data) {
            throw new Error(apiErrorDetail(data, "Error al guardar"));
          });
        }
        return response.json();
      })
      .then(function () {
        setStatus(currentCategoryId ? "Categoría actualizada" : "Categoría creada", "loading");
        clearCategoryForm();
        loadCategories();
      })
      .catch(function (error) {
        setStatus(error.message, "error");
      });
  }

  function handleCategoryAction(event) {
    const target = event.target;
    if (target.classList.contains("edit-category-btn")) {
      const categoryId = parseInt(target.getAttribute("data-id"), 10);
      const category = categoriesCache.find(function (c) { return c.id === categoryId; });
      if (category) fillCategoryForm(category);
    } else if (target.classList.contains("delete-category-btn")) {
      const categoryId = parseInt(target.getAttribute("data-id"), 10);
      if (!confirm("¿Eliminar esta categoría?")) return;
      setStatus("Eliminando...", "loading");
      fetch("/api/categories/" + categoryId, { method: "DELETE" })
        .then(function (response) {
          if (!response.ok) {
            return response.json().then(function (data) {
              throw new Error(apiErrorDetail(data, "Error al eliminar"));
            });
          }
          setStatus("Categoría eliminada", "loading");
          loadCategories();
        })
        .catch(function (error) {
          setStatus(error.message, "error");
        });
    }
  }

  function route() {
    const target = "#/" + DEFAULT_VIEW;
    if (window.location.hash !== target && currentView() === DEFAULT_VIEW) {
      window.location.hash = target;
      return;
    }
    activateView(currentView());
    const view = currentView();
    if (view === "dashboard") {
      loadDashboard();
    } else if (view === "sales") {
      loadProductsForSaleSelect();
      loadSales();
    } else if (view === "products") {
      loadProductsList();
    } else if (view === "categories") {
      loadCategories();
    }
  }

  if (sidebarToggleEl) {
    sidebarToggleEl.addEventListener("click", function () {
      document.querySelector(".sidebar").classList.toggle("collapsed");
    });
  }

  if (saleForm) {
    saleForm.addEventListener("submit", handleSaleSubmit);
  }

  if (productForm) {
    productForm.addEventListener("submit", handleProductSubmit);
  }

  if (productsTbody) {
    productsTbody.addEventListener("click", handleProductAction);
  }

  if (filterApplyBtn) {
    filterApplyBtn.addEventListener("click", applyFilters);
  }

  if (filterClearBtn) {
    filterClearBtn.addEventListener("click", clearFilters);
  }

  if (categoryForm) {
    categoryForm.addEventListener("submit", handleCategorySubmit);
  }

  if (categoryCancelBtn) {
    categoryCancelBtn.addEventListener("click", clearCategoryForm);
  }

  if (categoriesTbody) {
    categoriesTbody.addEventListener("click", handleCategoryAction);
  }

  window.addEventListener("hashchange", route);
  window.addEventListener("load", route);
})();