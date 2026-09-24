const state = { page: 1, size: 6, status: "" };

const listElement = document.getElementById("tripList");
const listStateElement = document.getElementById("listState");
const listStatusElement = document.getElementById("listStatus");
const pageMetaElement = document.getElementById("pageMeta");
const paginationElement = document.getElementById("pagination");
const filterElement = document.getElementById("statusFilter");
const formElement = document.getElementById("tripForm");
const formMessageElement = document.getElementById("formMessage");
const healthButtonElement = document.getElementById("healthButton");
const healthStatusElement = document.getElementById("healthStatus");
const statusLabels = { draft: "草稿", planned: "已规划", done: "已完成" };

function setListState(message, isError = false) {
  listStateElement.textContent = message;
  listStateElement.classList.toggle("error", isError);
}

function renderTrips(items) {
  if (!items.length) {
    listElement.innerHTML = "";
    setListState("没有符合条件的行程，可以从右侧创建一条。", false);
    return;
  }
  listStateElement.textContent = "";
  listElement.innerHTML = items.map((trip) => `
    <article class="trip-card">
      <div><h3>${escapeHtml(trip.title)}</h3><p>${escapeHtml(trip.destination)} · ${trip.days} 天 · ${statusLabels[trip.status] || trip.status}</p></div>
      <div class="trip-meta">¥ ${Number(trip.budget).toFixed(2)}<br>#${trip.id}</div>
      <div class="trip-actions"><button class="button danger" type="button" data-delete-trip="${trip.id}">删除</button></div>
    </article>
  `).join("");
  listElement.querySelectorAll("[data-delete-trip]").forEach((button) => {
    button.addEventListener("click", () => deleteTrip(Number(button.dataset.deleteTrip)));
  });
}

function renderPagination(pageCount) {
  paginationElement.innerHTML = "";
  for (let page = 1; page <= pageCount; page += 1) {
    const button = document.createElement("button");
    button.className = `page-button${page === state.page ? " active" : ""}`;
    button.type = "button";
    button.textContent = String(page);
    button.addEventListener("click", () => { state.page = page; loadTrips(); });
    paginationElement.appendChild(button);
  }
}

async function loadTrips() {
  setListState("正在加载行程…");
  listStatusElement.textContent = "请求中";
  const query = new URLSearchParams({ page: String(state.page), size: String(state.size) });
  if (state.status) query.set("status", state.status);
  try {
    const response = await fetch(`/api/trips?${query.toString()}`);
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    const result = await response.json();
    renderTrips(result.items);
    renderPagination(result.page_count);
    pageMetaElement.textContent = `${result.total} 条 · 第 ${result.page}/${result.page_count} 页`;
    listStatusElement.textContent = "已更新";
  } catch (error) {
    setListState(`加载失败：${error.message}。请检查后端是否启动。`, true);
    listStatusElement.textContent = "失败";
  }
}

async function createTrip(event) {
  event.preventDefault();
  formMessageElement.textContent = "";
  const formData = new FormData(formElement);
  const payload = {
    title: formData.get("title").trim(),
    destination: formData.get("destination").trim(),
    days: Number(formData.get("days")),
    budget: Number(formData.get("budget")),
    status: formData.get("status"),
  };
  try {
    const response = await fetch("/api/trips", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(payload) });
    const result = await response.json();
    if (!response.ok) throw new Error(result.detail?.[0]?.msg || result.detail || `HTTP ${response.status}`);
    formElement.reset();
    state.page = 1;
    await loadTrips();
  } catch (error) {
    formMessageElement.textContent = `保存失败：${error.message}`;
  }
}

async function deleteTrip(tripId) {
  if (!window.confirm("确定删除这条行程吗？")) return;
  const response = await fetch(`/api/trips/${tripId}`, { method: "DELETE" });
  if (!response.ok) { listStatusElement.textContent = "删除失败"; return; }
  await loadTrips();
}

function escapeHtml(value) {
  return String(value).replace(/[&<>'"]/g, (character) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", "'": "&#39;", '"': "&quot;" }[character]));
}

filterElement.addEventListener("change", () => { state.status = filterElement.value; state.page = 1; loadTrips(); });
document.getElementById("reloadButton").addEventListener("click", loadTrips);
formElement.addEventListener("submit", createTrip);
healthButtonElement.addEventListener("click", async () => {
  healthStatusElement.textContent = "检查中…";
  try {
    const response = await fetch("/healthz");
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    const result = await response.json();
    healthStatusElement.textContent = `服务正常：${result.status}`;
  } catch (error) {
    healthStatusElement.textContent = `服务检查失败：${error.message}`;
  }
});
loadTrips();
