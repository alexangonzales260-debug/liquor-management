"use strict";

(function () {
  const VIEWS = ["dashboard", "products", "sales"];
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

  function route() {
    const target = "#/" + DEFAULT_VIEW;
    if (window.location.hash !== target && currentView() === DEFAULT_VIEW) {
      window.location.hash = target;
      return;
    }
    activateView(currentView());
    if (currentView() === "dashboard") {
      loadDashboard();
    }
  }

  if (sidebarToggleEl) {
    sidebarToggleEl.addEventListener("click", function () {
      document.querySelector(".sidebar").classList.toggle("collapsed");
    });
  }

  window.addEventListener("hashchange", route);
  window.addEventListener("load", route);
})();