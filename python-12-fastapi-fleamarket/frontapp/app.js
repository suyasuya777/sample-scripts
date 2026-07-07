/* =========================================================================
   のみの市 — app.js
   Talks to the FastAPI fleamarket backend.

   ▸ Run the backend at  http://127.0.0.1:8000  (uvicorn main:app --reload)
   ▸ Serve THIS folder over http (Live Server などの http://127.0.0.1:5500 等)。
     接続先は下の API_BASE。バックエンドの CORS の allow_origins に、
     ブラウザで開いているオリジン（例 http://127.0.0.1:5500）を入れること。
   ========================================================================= */

const API_BASE = "http://127.0.0.1:8000";      // 127.0.0.1 を使う（localhost だと IPv6 解決で接続が固まる環境があるため）
const TOKEN_KEY = "fm_token";
const STATUS_LABEL = { ON_SALE: "出品中", SOLD_OUT: "売切れ" };

/* ---------------------------------------------------------------- state -- */
const state = {
  token: null,
  user: null,        // { user_id, username, exp }
  items: [],
  query: "",
  pendingDeleteId: null,
};

/* ----------------------------------------------------------- shortcuts --- */
const $  = (sel, root = document) => root.querySelector(sel);
const el = (tag, cls) => { const n = document.createElement(tag); if (cls) n.className = cls; return n; };

/* ============================================================ JWT utils == */
function parseJwt(token) {
  try {
    const payload = token.split(".")[1].replace(/-/g, "+").replace(/_/g, "/");
    const json = decodeURIComponent(
      atob(payload).split("").map(c => "%" + c.charCodeAt(0).toString(16).padStart(2, "0")).join("")
    );
    const p = JSON.parse(json);
    return { user_id: p.id, username: p.sub, exp: p.exp };
  } catch { return null; }
}

function loadToken() {
  const token = localStorage.getItem(TOKEN_KEY);
  if (!token) return;
  const user = parseJwt(token);
  if (!user || (user.exp && user.exp * 1000 < Date.now())) {   // expired / malformed
    localStorage.removeItem(TOKEN_KEY);
    return;
  }
  state.token = token;
  state.user = user;
}

function setToken(token) {
  localStorage.setItem(TOKEN_KEY, token);
  state.token = token;
  state.user = parseJwt(token);
}

function clearToken() {
  localStorage.removeItem(TOKEN_KEY);
  state.token = null;
  state.user = null;
}

/* ============================================================ API client = */
class ApiError extends Error {
  constructor(message, status) { super(message); this.status = status; }
}

/* Turn a FastAPI error body into a readable Japanese-friendly string. */
function describeError(payload, status) {
  if (payload && typeof payload.detail === "string") return payload.detail;
  if (payload && Array.isArray(payload.detail)) {           // 422 validation
    return payload.detail.map(d => {
      const field = Array.isArray(d.loc) ? d.loc[d.loc.length - 1] : "入力";
      return `${field}: ${d.msg}`;
    }).join(" / ");
  }
  return `エラーが発生しました（HTTP ${status}）`;
}

async function api(path, { method = "GET", json, form, auth = false } = {}) {
  const headers = {};
  let body;

  if (json !== undefined) { headers["Content-Type"] = "application/json"; body = JSON.stringify(json); }
  if (form !== undefined) { headers["Content-Type"] = "application/x-www-form-urlencoded"; body = new URLSearchParams(form).toString(); }
  if (auth) {
    if (!state.token) throw new ApiError("ログインが必要です", 401);
    headers["Authorization"] = `Bearer ${state.token}`;
  }

  let res;
  try {
    res = await fetch(`${API_BASE}${path}`, { method, headers, body });
  } catch {
    throw new ApiError(`サーバーに接続できません（${API_BASE}）。バックエンドが起動しているか確認してください。`, 0);
  }

  if (res.status === 401 && auth) {     // token went stale mid-session
    clearToken(); renderAccount(); renderItems();
    throw new ApiError("セッションが切れました。もう一度ログインしてください。", 401);
  }

  let payload = null;
  const text = await res.text();
  if (text) { try { payload = JSON.parse(text); } catch { payload = text; } }

  if (!res.ok) throw new ApiError(describeError(payload, res.status), res.status);
  return payload;
}

/* ========================================================= data actions == */
async function loadItems() {
  const grid = $("#grid");
  grid.setAttribute("aria-busy", "true");
  renderSkeleton();
  try {
    const q = state.query.trim();
    const path = q.length >= 1 ? `/items?name=${encodeURIComponent(q)}` : "/items";
    state.items = await api(path);
    renderItems();
  } catch (err) {
    renderLoadError(err.message);
  } finally {
    grid.setAttribute("aria-busy", "false");
  }
}

/* ============================================================== rendering = */
function money(n) { return Number(n).toLocaleString("ja-JP"); }

function formatDate(iso) {
  const d = new Date(iso);
  if (isNaN(d)) return "";
  return `${d.getFullYear()}/${String(d.getMonth() + 1).padStart(2, "0")}/${String(d.getDate()).padStart(2, "0")}`;
}

function renderAccount() {
  const area = $("#account-area");
  area.innerHTML = "";
  if (state.user) {
    const chip = el("span", "user-chip");
    chip.innerHTML = `<span class="user-chip__dot"></span>${escapeHtml(state.user.username)}`;
    const out = el("button", "btn btn--ghost btn--sm");
    out.textContent = "ログアウト";
    out.addEventListener("click", logout);
    area.append(chip, out);
  } else {
    const login = el("button", "btn btn--ghost");
    login.textContent = "ログイン / 新規登録";
    login.addEventListener("click", () => openAuth("login"));
    area.append(login);
  }
}

function renderSkeleton() {
  const grid = $("#grid");
  $("#empty").hidden = true;
  grid.innerHTML = "";
  for (let i = 0; i < 6; i++) {
    const c = el("article", "card skeleton");
    c.innerHTML = `
      <div class="sk sk--title"></div>
      <div class="sk sk--line"></div>
      <div class="sk sk--line short"></div>
      <div class="sk sk--tag" style="margin-top:auto"></div>`;
    grid.append(c);
  }
}

function renderLoadError(message) {
  const grid = $("#grid");
  grid.innerHTML = "";
  const empty = $("#empty");
  $("#empty-title").textContent = "読み込めませんでした";
  $("#empty-text").textContent = message;
  $("#empty-sell-btn").hidden = true;
  empty.hidden = false;
  setCount(null);
}

function setCount(n) {
  const badge = $("#count");
  if (n === null) { badge.hidden = true; return; }
  badge.textContent = `${n}件`;
  badge.hidden = false;
}

function renderItems() {
  const grid = $("#grid");
  const empty = $("#empty");
  grid.innerHTML = "";

  setCount(state.items.length);

  if (state.items.length === 0) {
    $("#empty-sell-btn").hidden = false;
    if (state.query.trim().length >= 1) {
      $("#empty-title").textContent = "見つかりませんでした";
      $("#empty-text").textContent = `「${state.query.trim()}」に当てはまる品物はありません。別の言葉で探してみてください。`;
      $("#empty-sell-btn").hidden = true;
    } else {
      $("#empty-title").textContent = "まだ出品がありません";
      $("#empty-text").textContent = "最初の品物を並べて、市を始めましょう。";
    }
    empty.hidden = false;
    return;
  }

  empty.hidden = true;
  const mine = state.user?.user_id;
  for (const item of state.items) {
    grid.append(renderCard(item, item.user_id === mine));
  }
}

function renderCard(item, isMine) {
  const sold = item.status === "SOLD_OUT";
  const card = el("article", "card" + (isMine ? " is-mine" : "") + (sold ? " is-sold" : ""));

  const head = el("div", "card__head");
  const name = el("h3", "card__name");
  name.textContent = item.name;
  const pill = el("span", "pill " + (sold ? "pill--soldout" : "pill--onsale"));
  pill.textContent = STATUS_LABEL[item.status] ?? item.status;
  head.append(name, pill);

  const desc = el("p", "card__desc" + (item.description ? "" : " is-empty"));
  desc.textContent = item.description || "説明はありません";

  const tagrow = el("div", "card__tagrow");
  const tag = el("span", "price-tag");
  tag.innerHTML = `<span class="price-tag__yen">¥</span><span class="price-tag__num">${money(item.price)}</span>`;
  const date = el("span", "card__owner");
  date.textContent = formatDate(item.created_at);
  tagrow.append(tag, date);

  const foot = el("div", "card__foot");
  const owner = el("span", "card__owner" + (isMine ? " is-me" : ""));
  owner.textContent = isMine ? "あなたの出品" : `出品者 #${item.user_id}`;
  foot.append(owner);

  if (isMine) {
    const actions = el("div", "card__actions");
    const edit = el("button", "icon-btn");
    edit.textContent = "編集";
    edit.addEventListener("click", () => openItemDialog(item));
    const del = el("button", "icon-btn icon-btn--danger");
    del.textContent = "削除";
    del.addEventListener("click", () => openConfirm(item));
    actions.append(edit, del);
    foot.append(actions);
  }

  card.append(head, desc, tagrow, foot);
  if (sold) { const s = el("span", "stamp"); s.textContent = "SOLD"; card.append(s); }
  return card;
}

function escapeHtml(s) {
  return String(s).replace(/[&<>"']/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
}

/* ============================================================ AUTH dialog = */
const authDialog = $("#auth-dialog");
let authMode = "login";

function openAuth(mode = "login", note = "") {
  setAuthMode(mode);
  const noteEl = $("#auth-note");
  noteEl.textContent = note;
  noteEl.hidden = !note;
  $("#auth-error").hidden = true;
  $("#auth-form").reset();
  if (!authDialog.open) authDialog.showModal();
  setTimeout(() => $("#auth-username").focus(), 50);
}

function setAuthMode(mode) {
  authMode = mode;
  $("#tab-login").setAttribute("aria-selected", String(mode === "login"));
  $("#tab-signup").setAttribute("aria-selected", String(mode === "signup"));
  $("#auth-title").textContent = mode === "login" ? "おかえりなさい" : "はじめまして";
  $("#auth-submit").textContent = mode === "login" ? "ログイン" : "登録してはじめる";
  $("#auth-password").setAttribute("autocomplete", mode === "login" ? "current-password" : "new-password");
  $("#auth-error").hidden = true;
}

let authBusy = false;   // click と submit の二重発火を防ぐガード
async function submitAuth(e) {
  if (e) e.preventDefault();
  if (authBusy) return;          // 既に処理中なら無視
  const username = $("#auth-username").value.trim();
  const password = $("#auth-password").value;
  const errEl = $("#auth-error");
  const btn = $("#auth-submit");

  if (username.length < 2) return showFieldError(errEl, "ユーザー名は2文字以上で入力してください。");
  if (password.length < 8) return showFieldError(errEl, "パスワードは8文字以上で入力してください。");

  authBusy = true;
  btn.disabled = true;
  const original = btn.textContent;
  btn.textContent = "処理中…";
  try {
    if (authMode === "signup") {
      await api("/auth/signup", { method: "POST", json: { username, password } });
    }
    // both flows end with a login to obtain the token
    const tok = await api("/auth/login", { method: "POST", form: { username, password } });
    setToken(tok.access_token);
    authDialog.close();
    renderAccount();
    renderItems();
    toast(authMode === "signup" ? `ようこそ、${username} さん` : `ログインしました`, "ok");
  } catch (err) {
    // ▼ 本当の失敗原因を必ず見えるようにする（Console とダイアログの両方へ）
    console.error("[auth] 失敗:", { mode: authMode, status: err.status, message: err.message }, err);
    const where = authMode === "signup" ? "新規登録" : "ログイン";
    showFieldError(errEl, `${where}に失敗：${err.message}（status=${err.status ?? "?"}）`);
  } finally {
    authBusy = false;
    btn.disabled = false;
    btn.textContent = original;
  }
}

function showFieldError(elem, msg) { elem.textContent = msg; elem.hidden = false; }

function logout() {
  clearToken();
  renderAccount();
  renderItems();
  toast("ログアウトしました", "ok");
}

/* ============================================================ ITEM dialog = */
const itemDialog = $("#item-dialog");
let editingId = null;

function openItemDialog(item = null) {
  if (!state.user) { openAuth("login", "出品にはログインが必要です。"); return; }

  editingId = item ? item.id : null;
  const editing = Boolean(item);

  $("#item-title").textContent = editing ? "出品を編集" : "出品する";
  $("#item-sub").textContent = editing ? "内容を変更して保存します。" : "品物の情報を入力してください。";
  $("#item-submit").textContent = editing ? "変更を保存" : "この内容で出品する";
  $("#status-field").hidden = !editing;     // status can only be changed on edit
  $("#item-error").hidden = true;

  $("#item-name").value  = item ? item.name : "";
  $("#item-price").value = item ? item.price : "";
  $("#item-desc").value  = item ? (item.description ?? "") : "";
  $("#item-status").value = item ? item.status : "ON_SALE";

  clearInvalid();
  if (!itemDialog.open) itemDialog.showModal();
  setTimeout(() => $("#item-name").focus(), 50);
}

function clearInvalid() {
  ["#item-name", "#item-price", "#item-desc"].forEach(s => $(s).classList.remove("is-invalid"));
}

async function submitItem(e) {
  e.preventDefault();
  const errEl = $("#item-error");
  clearInvalid();

  const name = $("#item-name").value.trim();
  const priceRaw = $("#item-price").value;
  const description = $("#item-desc").value.trim();
  const price = Number(priceRaw);

  if (name.length < 2 || name.length > 50) { $("#item-name").classList.add("is-invalid"); return showFieldError(errEl, "品名は2〜50文字で入力してください。"); }
  if (!Number.isInteger(price) || price < 1) { $("#item-price").classList.add("is-invalid"); return showFieldError(errEl, "価格は1円以上の整数で入力してください。"); }
  if (description.length > 255) { $("#item-desc").classList.add("is-invalid"); return showFieldError(errEl, "説明は255文字までです。"); }

  const btn = $("#item-submit");
  btn.disabled = true;
  const original = btn.textContent;
  btn.textContent = "保存中…";
  try {
    if (editingId === null) {
      await api("/items", { method: "POST", auth: true, json: { name, price, description: description || null } });
      toast("出品しました", "ok");
    } else {
      const status = $("#item-status").value;
      await api(`/items/${editingId}`, { method: "PUT", auth: true, json: { name, price, description: description || null, status } });
      toast("変更を保存しました", "ok");
    }
    itemDialog.close();
    await loadItems();
  } catch (err) {
    showFieldError(errEl, err.message);
  } finally {
    btn.disabled = false;
    btn.textContent = original;
  }
}

/* ============================================================ CONFIRM ===== */
const confirmDialog = $("#confirm-dialog");

function openConfirm(item) {
  state.pendingDeleteId = item.id;
  $("#confirm-name").textContent = item.name;
  confirmDialog.showModal();
}

async function doDelete() {
  const id = state.pendingDeleteId;
  if (id == null) return;
  const btn = $("#confirm-ok");
  btn.disabled = true;
  btn.textContent = "削除中…";
  try {
    await api(`/items/${id}`, { method: "DELETE", auth: true });
    confirmDialog.close();
    toast("出品を取り下げました", "ok");
    await loadItems();
  } catch (err) {
    confirmDialog.close();
    toast(err.message, "error");
  } finally {
    btn.disabled = false;
    btn.textContent = "削除する";
    state.pendingDeleteId = null;
  }
}

/* ============================================================== TOASTS ==== */
function toast(message, type = "") {
  const t = el("div", "toast" + (type ? ` toast--${type}` : ""));
  t.innerHTML = `<span class="toast__dot"></span>${escapeHtml(message)}`;
  $("#toasts").append(t);
  setTimeout(() => { t.style.opacity = "0"; t.style.transform = "translateY(8px)"; setTimeout(() => t.remove(), 250); }, 3200);
}

/* ============================================================== WIRING ==== */
function debounce(fn, ms) { let id; return (...a) => { clearTimeout(id); id = setTimeout(() => fn(...a), ms); }; }

function init() {
  loadToken();
  renderAccount();
  loadItems();

  // search（1文字以上で検索）
  $("#search-input").addEventListener("input", debounce((e) => {
    $("#searching-label").hidden = true;
    state.query = e.target.value;
    loadItems();
  }, 350));

  // sell buttons
  $("#sell-btn").addEventListener("click", () => openItemDialog());
  $("#empty-sell-btn").addEventListener("click", () => openItemDialog());

  // auth dialog
  $("#tab-login").addEventListener("click", () => setAuthMode("login"));
  $("#tab-signup").addEventListener("click", () => setAuthMode("signup"));
  $("#auth-form").addEventListener("submit", (e) => { e.preventDefault(); submitAuth(e); });
  $("#auth-submit").addEventListener("click", (e) => { e.preventDefault(); submitAuth(e); });

  // item dialog
  $("#item-form").addEventListener("submit", submitItem);

  // confirm
  $("#confirm-ok").addEventListener("click", doDelete);

  // generic close buttons + click-on-backdrop for all dialogs
  document.querySelectorAll("dialog").forEach(dlg => {
    dlg.querySelectorAll("[data-close]").forEach(b => b.addEventListener("click", () => dlg.close()));
    dlg.addEventListener("click", (e) => { if (e.target === dlg) dlg.close(); });   // backdrop click
  });
}

document.addEventListener("DOMContentLoaded", init);
