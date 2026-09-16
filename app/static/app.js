"use strict";

(function () {
  const VIEWS = ["dashboard", "products", "sales", "categories", "restocks", "suppliers", "purchase-orders"];
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
  const categorySelect = document.querySelector("#category");

  const categoryForm = document.querySelector("#category-form");
  const categoryNameInput = document.querySelector("#category-name");
  const categoryDescInput = document.querySelector("#category-description");
  const categorySubmitBtn = document.querySelector("#category-submit");
  const categoryCancelBtn = document.querySelector("#category-cancel");
  const categoriesTbody = document.querySelector("#categories-tbody");

  const restockForm = document.querySelector("#restock-form");
  const restockProductSelect = document.querySelector("#restock-product");
  const restockQtyInput = document.querySelector("#restock-qty");
  const restockUnitCostInput = document.querySelector("#restock-unit-cost");
  const restockNotesInput = document.querySelector("#restock-notes");
  const restocksTableBody = document.querySelector("#restocks-table tbody");

  const supplierForm = document.querySelector("#supplier-form");
  const supplierNameInput = document.querySelector("#supplier-name");
  const supplierContactInput = document.querySelector("#supplier-contact");
  const supplierEmailInput = document.querySelector("#supplier-email");
  const supplierPhoneInput = document.querySelector("#supplier-phone");
  const supplierAddressInput = document.querySelector("#supplier-address");
  const supplierTaxIdInput = document.querySelector("#supplier-tax-id");
  const supplierNotesInput = document.querySelector("#supplier-notes");
  const supplierSubmitBtn = document.querySelector("#supplier-submit");
  const supplierCancelBtn = document.querySelector("#supplier-cancel");
  const suppliersTbody = document.querySelector("#suppliers-tbody");

  const poFilterStatus = document.querySelector("#po-filter-status");
  const poFilterSupplier = document.querySelector("#po-filter-supplier");
  const poFilterSearch = document.querySelector("#po-filter-search");
  const poFilterApplyBtn = document.querySelector("#po-filter-apply");
  const poFilterClearBtn = document.querySelector("#po-filter-clear");
  const poTbody = document.querySelector("#purchase-orders-tbody");
  const poReceiveModal = document.querySelector("#po-receive-modal");
  const poReceiveForm = document.querySelector("#po-receive-form");
  const poReceiveIdInput = document.querySelector("#po-receive-id");
  const poReceiveQtyInput = document.querySelector("#po-receive-qty");
  const poReceiveCancelBtn = document.querySelector("#po-receive-cancel");
  const poCancelModal = document.querySelector("#po-cancel-modal");
  const poCancelConfirmBtn = document.querySelector("#po-cancel-confirm");
  const poCancelDismissBtn = document.querySelector("#po-cancel-dismiss");

  let currentProductId = null;
  let productsCache = [];
  let currentCategoryId = null;
  let categoriesCache = [];
  let pendingRestockProductName = null;
  let currentSupplierId = null;
  let suppliersCache = [];
  let poCache = [];
  let pendingPOCancelId = null;

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
        '<tr><td colspan="3" class="empty-row">Sin productos con stock bajo</td></tr>';
      return;
    }
    rows.forEach(function (row) {
      const tr = document.createElement("tr");
      const name = document.createElement("td");
      name.textContent = row.name;
      const stock = document.createElement("td");
      stock.textContent = row.stock;
      const actions = document.createElement("td");
      actions.className = "actions";
      const button = document.createElement("button");
      button.type = "button";
      button.className = "secondary restock-btn";
      button.textContent = "Reponer";
      button.addEventListener("click", function () {
        pendingRestockProductName = row.name;
        window.location.hash = "#/restocks";
      });
      actions.appendChild(button);
      tr.append(name, stock, actions);
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
    categorySelect.value = "";
    currentProductId = null;
    productSubmitBtn.textContent = "Guardar";
    productForm.querySelectorAll("input").forEach(function (input) {
      input.removeAttribute("disabled");
    });
  }

  function fillProductForm(product) {
    currentProductId = product.id;
    document.querySelector("#name").value = product.name;
    categorySelect.value = product.category || "";
    document.querySelector("#volume_ml").value = product.volume_ml || "";
    document.querySelector("#price_cents").value = product.price_cents !== null ? product.price_cents : "";
    document.querySelector("#stock").value = product.stock;
    productSubmitBtn.textContent = "Actualizar";
  }

  function handleProductSubmit(event) {
    event.preventDefault();
    const payload = {
      name: document.querySelector("#name").value.trim(),
      category: categorySelect.value.trim() || null,
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

  function loadCategoriesForProductSelects() {
    if (!categorySelect || !filterCategory) {
      return;
    }
    fetch("/api/categories")
      .then(function (response) {
        if (!response.ok) throw new Error("Failed to load categories");
        return response.json();
      })
      .then(function (categories) {
        function buildOptions(defaultLabel) {
          const fragment = document.createDocumentFragment();
          const defaultOption = document.createElement("option");
          defaultOption.value = "";
          defaultOption.textContent = defaultLabel;
          fragment.appendChild(defaultOption);
          categories.forEach(function (category) {
            const option = document.createElement("option");
            option.value = category.name;
            option.textContent = category.name;
            fragment.appendChild(option);
          });
          return fragment;
        }
        categorySelect.textContent = "";
        categorySelect.appendChild(buildOptions("-- Sin categoría --"));
        filterCategory.textContent = "";
        filterCategory.appendChild(buildOptions("Todas las categorías"));
      })
      .catch(function () {
        setStatus("Error al cargar categorías", "error");
      });
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
        loadCategoriesForProductSelects();
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

  function loadProductsForRestockSelect() {
    fetch("/api/products")
      .then(function (response) {
        if (!response.ok) throw new Error("Failed to load products");
        return response.json();
      })
      .then(function (products) {
        productsCache = products;
        restockProductSelect.innerHTML = '<option value="">Seleccionar producto...</option>';
        products.forEach(function (product) {
          const option = document.createElement("option");
          option.value = product.id;
          option.textContent = product.name + (product.category ? " (" + product.category + ")" : "") + " - Stock: " + product.stock;
          restockProductSelect.appendChild(option);
        });
        if (pendingRestockProductName) {
          const selected = products.find(function (p) {
            return p.name === pendingRestockProductName;
          });
          if (selected) {
            restockProductSelect.value = String(selected.id);
            if (restockQtyInput) {
              restockQtyInput.focus();
            }
          }
          pendingRestockProductName = null;
        }
      })
      .catch(function () {
        setStatus("Error al cargar productos", "error");
      });
  }

  function loadRestocks() {
    if (!statusEl || !restocksTableBody) {
      return;
    }
    setStatus("Cargando reposiciones...", "loading");
    fetch("/api/restocks")
      .then(function (response) {
        if (!response.ok) throw new Error("Failed to load restocks");
        return response.json();
      })
      .then(function (restocks) {
        restocksTableBody.innerHTML = "";
        if (!restocks.length) {
          restocksTableBody.innerHTML =
            '<tr><td colspan="7" class="empty-row">Sin reposiciones registradas</td></tr>';
          setStatus("");
          return;
        }
        restocks.forEach(function (restock) {
          const tr = document.createElement("tr");
          const product = productsCache.find(function (p) { return p.id === restock.product_id; });
          const productName = product ? product.name : "Desconocido";
          tr.innerHTML =
            "<td>" + restock.id + "</td>" +
            "<td>" + productName + "</td>" +
            "<td>" + restock.qty + "</td>" +
            "<td>" + (restock.unit_cost_cents !== null ? formatMoney(restock.unit_cost_cents) : "") + "</td>" +
            "<td>" + (restock.total_cost_cents !== null ? formatMoney(restock.total_cost_cents) : "") + "</td>" +
            "<td>" + (restock.notes || "") + "</td>" +
            "<td>" + formatDate(restock.created_at) + "</td>";
          restocksTableBody.appendChild(tr);
        });
        setStatus("");
      })
      .catch(function () {
        setStatus("Error al cargar reposiciones", "error");
      });
  }

  function handleRestockSubmit(event) {
    event.preventDefault();
    const productId = parseInt(restockProductSelect.value, 10);
    const qty = parseInt(restockQtyInput.value, 10);
    const unitCostValue = restockUnitCostInput.value.trim();
    const unitCostCents = unitCostValue === "" ? null : parseInt(unitCostValue, 10);
    const notes = restockNotesInput.value.trim() || null;

    if (!productId || isNaN(qty) || qty < 1) {
      setStatus("Selecciona un producto y una cantidad válida", "error");
      return;
    }

    setStatus("Registrando reposición...", "loading");
    fetch("/api/restocks", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        product_id: productId,
        qty: qty,
        unit_cost_cents: unitCostCents,
        notes: notes,
      }),
    })
      .then(function (response) {
        if (!response.ok) {
          return response.json().then(function (data) {
            throw new Error(apiErrorDetail(data, "Error al registrar reposición"));
          });
        }
        return response.json();
      })
      .then(function () {
        setStatus("Reposición registrada", "loading");
        restockForm.reset();
        restockQtyInput.value = "1";
        loadProductsForRestockSelect();
        loadRestocks();
        loadDashboard();
      })
      .catch(function (error) {
        setStatus(error.message, "error");
      });
  }

  function loadSuppliers() {
    if (!statusEl || !suppliersTbody) {
      return;
    }
    setStatus("Cargando proveedores...", "loading");
    fetch("/api/suppliers")
      .then(function (response) {
        if (!response.ok) throw new Error("Failed to load suppliers");
        return response.json();
      })
      .then(function (suppliers) {
        suppliersCache = suppliers;
        renderSuppliersTable(suppliers);
        setStatus("");
      })
      .catch(function () {
        setStatus("Error al cargar proveedores", "error");
      });
  }

  function renderSuppliersTable(suppliers) {
    suppliersTbody.innerHTML = "";
    if (!suppliers.length) {
      suppliersTbody.innerHTML =
        '<tr><td colspan="7" class="empty-row">Sin proveedores</td></tr>';
      return;
    }
    suppliers.forEach(function (supplier) {
      const tr = document.createElement("tr");
      tr.innerHTML =
        "<td>" + supplier.id + "</td>" +
        "<td>" + (supplier.name || "") + "</td>" +
        "<td>" + (supplier.contact_person || "") + "</td>" +
        "<td>" + (supplier.email || "") + "</td>" +
        "<td>" + (supplier.phone || "") + "</td>" +
        "<td>" + (supplier.address || "") + "</td>" +
        '<td class="actions">' +
          '<button type="button" class="edit-supplier-btn" data-id="' + supplier.id + '">Editar</button>' +
          '<button type="button" class="danger delete-supplier-btn" data-id="' + supplier.id + '">Eliminar</button>' +
        "</td>";
      suppliersTbody.appendChild(tr);
    });
  }

  function clearSupplierForm() {
    supplierForm.reset();
    currentSupplierId = null;
    supplierSubmitBtn.textContent = "Guardar";
    supplierCancelBtn.classList.add("hidden");
  }

  function fillSupplierForm(supplier) {
    currentSupplierId = supplier.id;
    supplierNameInput.value = supplier.name;
    supplierContactInput.value = supplier.contact_person || "";
    supplierEmailInput.value = supplier.email || "";
    supplierPhoneInput.value = supplier.phone || "";
    supplierAddressInput.value = supplier.address || "";
    supplierTaxIdInput.value = supplier.tax_id || "";
    supplierNotesInput.value = supplier.notes || "";
    supplierSubmitBtn.textContent = "Actualizar";
    supplierCancelBtn.classList.remove("hidden");
  }

  function handleSupplierSubmit(event) {
    event.preventDefault();
    const payload = {
      name: supplierNameInput.value.trim(),
      contact_person: supplierContactInput.value.trim() || null,
      email: supplierEmailInput.value.trim() || null,
      phone: supplierPhoneInput.value.trim() || null,
      address: supplierAddressInput.value.trim() || null,
      tax_id: supplierTaxIdInput.value.trim() || null,
      notes: supplierNotesInput.value.trim() || null,
    };

    if (!payload.name) {
      setStatus("El nombre es obligatorio", "error");
      return;
    }

    const url = currentSupplierId ? "/api/suppliers/" + currentSupplierId : "/api/suppliers";
    const method = currentSupplierId ? "PUT" : "POST";

    setStatus(currentSupplierId ? "Actualizando..." : "Guardando...", "loading");
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
        setStatus(currentSupplierId ? "Proveedor actualizado" : "Proveedor creado", "loading");
        clearSupplierForm();
        loadSuppliers();
      })
      .catch(function (error) {
        setStatus(error.message, "error");
      });
  }

  function handleSupplierAction(event) {
    const target = event.target;
    if (target.classList.contains("edit-supplier-btn")) {
      const supplierId = parseInt(target.getAttribute("data-id"), 10);
      const supplier = suppliersCache.find(function (s) { return s.id === supplierId; });
      if (supplier) fillSupplierForm(supplier);
    } else if (target.classList.contains("delete-supplier-btn")) {
      const supplierId = parseInt(target.getAttribute("data-id"), 10);
      if (!confirm("¿Eliminar este proveedor?")) return;
      setStatus("Eliminando...", "loading");
      fetch("/api/suppliers/" + supplierId, { method: "DELETE" })
        .then(function (response) {
          if (response.status === 409) {
            return response.json().then(function (data) {
              throw new Error(apiErrorDetail(data, "No se puede eliminar el proveedor"));
            });
          }
          if (!response.ok) {
            return response.json().then(function (data) {
              throw new Error(apiErrorDetail(data, "Error al eliminar"));
            });
          }
          setStatus("Proveedor eliminado", "loading");
          clearSupplierForm();
          loadSuppliers();
        })
        .catch(function (error) {
          setStatus(error.message, "error");
        });
    }
  }

  function statusBadge(status) {
    const labels = {
      pending: "Pendiente",
      partial: "Parcial",
      received: "Recibida",
      cancelled: "Cancelada",
    };
    return (
      '<span class="status-badge status-' + status + '">' +
      (labels[status] || status) +
      "</span>"
    );
  }

  function renderPOSupplierFilter() {
    poFilterSupplier.innerHTML = '<option value="">Todos los proveedores</option>';
    suppliersCache.forEach(function (supplier) {
      const option = document.createElement("option");
      option.value = supplier.id;
      option.textContent = supplier.name;
      poFilterSupplier.appendChild(option);
    });
  }

  function loadPOFilters() {
    if (!poFilterSupplier) {
      return;
    }
    if (suppliersCache.length) {
      renderPOSupplierFilter();
      return;
    }
    fetch("/api/suppliers")
      .then(function (response) {
        if (!response.ok) throw new Error("Failed to load suppliers");
        return response.json();
      })
      .then(function (suppliers) {
        suppliersCache = suppliers;
        renderPOSupplierFilter();
      })
      .catch(function () {
        setStatus("Error al cargar proveedores", "error");
      });
  }

  function loadPurchaseOrders() {
    if (!statusEl || !poTbody) {
      return;
    }
    const params = new URLSearchParams();
    const status = poFilterStatus.value.trim();
    const supplierId = poFilterSupplier.value.trim();
    const q = poFilterSearch.value.trim();
    if (status) params.append("status", status);
    if (supplierId) params.append("supplier_id", supplierId);
    if (q) params.append("q", q);

    setStatus("Cargando órdenes de compra...", "loading");
    fetch("/api/purchase-orders?" + params.toString())
      .then(function (response) {
        if (!response.ok) throw new Error("Failed to load purchase orders");
        return response.json();
      })
      .then(function (orders) {
        poCache = orders;
        renderPurchaseOrdersTable(orders);
        setStatus("");
      })
      .catch(function () {
        setStatus("Error al cargar órdenes de compra", "error");
      });
  }

  function renderPurchaseOrdersTable(orders) {
    poTbody.innerHTML = "";
    if (!orders.length) {
      poTbody.innerHTML =
        '<tr><td colspan="11" class="empty-row">Sin órdenes de compra</td></tr>';
      return;
    }
    orders.forEach(function (order) {
      const tr = document.createElement("tr");
      let actions = '<td class="actions">';
      if (order.status === "pending" || order.status === "partial") {
        actions +=
          '<button type="button" class="receive-po-btn" data-id="' +
          order.id +
          '">Recibir</button>';
      }
      if (order.status === "pending") {
        actions +=
          '<button type="button" class="danger cancel-po-btn" data-id="' +
          order.id +
          '">Cancelar</button>';
      }
      actions += "</td>";
      tr.innerHTML =
        "<td>" + order.id + "</td>" +
        "<td>" + (order.supplier_name || "") + "</td>" +
        "<td>" + (order.product_name || "") + "</td>" +
        "<td>" + order.qty_ordered + "</td>" +
        "<td>" + order.qty_received + "</td>" +
        "<td>" + formatMoney(order.unit_cost_cents) + "</td>" +
        "<td>" + formatMoney(order.total_cost_cents) + "</td>" +
        "<td>" + statusBadge(order.status) + "</td>" +
        "<td>" + formatDate(order.order_date) + "</td>" +
        "<td>" + (order.expected_date ? formatDate(order.expected_date) : "") + "</td>" +
        actions;
      poTbody.appendChild(tr);
    });
  }

  function handlePOReceive(poId) {
    const order = poCache.find(function (o) {
      return o.id === poId;
    });
    if (!order || !poReceiveModal) {
      return;
    }
    poReceiveIdInput.value = order.id;
    const pendingQty = order.qty_ordered - order.qty_received;
    poReceiveQtyInput.max = pendingQty;
    poReceiveQtyInput.value = pendingQty;
    poReceiveModal.classList.remove("hidden");
    poReceiveQtyInput.focus();
  }

  function closePOReceiveModal() {
    if (poReceiveModal) {
      poReceiveModal.classList.add("hidden");
    }
  }

  function submitPOReceive(event) {
    event.preventDefault();
    const poId = parseInt(poReceiveIdInput.value, 10);
    const qtyReceived = parseInt(poReceiveQtyInput.value, 10);
    if (!poId || isNaN(qtyReceived) || qtyReceived < 1) {
      setStatus("Ingresa una cantidad válida", "error");
      return;
    }
    setStatus("Recibiendo mercancía...", "loading");
    fetch("/api/purchase-orders/" + poId + "/receive", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ qty_received: qtyReceived }),
    })
      .then(function (response) {
        if (!response.ok) {
          return response.json().then(function (data) {
            throw new Error(apiErrorDetail(data, "Error al recibir mercancía"));
          });
        }
        return response.json();
      })
      .then(function () {
        closePOReceiveModal();
        setStatus("Mercancía recibida", "loading");
        loadPurchaseOrders();
        loadDashboard();
        loadProductsForRestockSelect();
        loadProductsForSaleSelect();
      })
      .catch(function (error) {
        setStatus(error.message, "error");
      });
  }

  function handlePOCancel(poId) {
    if (!confirm("¿Cancelar esta orden de compra?")) {
      return;
    }
    setStatus("Cancelando orden...", "loading");
    fetch("/api/purchase-orders/" + poId, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ status: "cancelled" }),
    })
      .then(function (response) {
        if (!response.ok) {
          return response.json().then(function (data) {
            throw new Error(apiErrorDetail(data, "Error al cancelar orden"));
          });
        }
        return response.json();
      })
      .then(function () {
        setStatus("Orden cancelada", "loading");
        loadPurchaseOrders();
      })
      .catch(function (error) {
        setStatus(error.message, "error");
      });
  }

  function closePOCancelModal() {
    if (poCancelModal) {
      poCancelModal.classList.add("hidden");
    }
  }

  function handlePOAction(event) {
    const target = event.target;
    if (target.classList.contains("receive-po-btn")) {
      handlePOReceive(parseInt(target.getAttribute("data-id"), 10));
    } else if (target.classList.contains("cancel-po-btn")) {
      pendingPOCancelId = parseInt(target.getAttribute("data-id"), 10);
      if (poCancelModal) {
        poCancelModal.classList.remove("hidden");
      } else {
        handlePOCancel(pendingPOCancelId);
      }
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
      loadCategoriesForProductSelects();
      loadProductsList();
    } else if (view === "categories") {
      loadCategories();
    } else if (view === "restocks") {
      loadProductsForRestockSelect();
      loadRestocks();
    } else if (view === "suppliers") {
      loadSuppliers();
    } else if (view === "purchase-orders") {
      loadPOFilters();
      loadPurchaseOrders();
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

  if (restockForm) {
    restockForm.addEventListener("submit", handleRestockSubmit);
  }

  if (supplierForm) {
    supplierForm.addEventListener("submit", handleSupplierSubmit);
  }

  if (supplierCancelBtn) {
    supplierCancelBtn.addEventListener("click", clearSupplierForm);
  }

  if (suppliersTbody) {
    suppliersTbody.addEventListener("click", handleSupplierAction);
  }

  if (poFilterApplyBtn) {
    poFilterApplyBtn.addEventListener("click", loadPurchaseOrders);
  }

  if (poFilterClearBtn) {
    poFilterClearBtn.addEventListener("click", function () {
      poFilterStatus.value = "";
      poFilterSupplier.value = "";
      poFilterSearch.value = "";
      loadPurchaseOrders();
    });
  }

  if (poTbody) {
    poTbody.addEventListener("click", handlePOAction);
  }

  if (poReceiveForm) {
    poReceiveForm.addEventListener("submit", submitPOReceive);
  }

  if (poReceiveCancelBtn) {
    poReceiveCancelBtn.addEventListener("click", closePOReceiveModal);
  }

  if (poCancelConfirmBtn) {
    poCancelConfirmBtn.addEventListener("click", function () {
      closePOCancelModal();
      if (pendingPOCancelId) {
        handlePOCancel(pendingPOCancelId);
      }
    });
  }

  if (poCancelDismissBtn) {
    poCancelDismissBtn.addEventListener("click", closePOCancelModal);
  }

  window.addEventListener("hashchange", route);
  window.addEventListener("load", route);
})();