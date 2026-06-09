/**
 * API E2E Test Console - app.js
 * FastAPI (Users / Items) エンドポイントのE2Eテスト用フロントエンド
 */

const App = (() => {

  // ── 状態 ───────────────────────────────────────────
  let currentTab = 'users-list';

  // ── エンドポイント定義 ──────────────────────────────
  const ENDPOINTS = {
    'users-list':   { method: 'GET',    path: () => '/users',                   body: null },
    'users-paged':  { method: 'GET',    path: () => buildPaged('/users/paged', 'users-paged-skip', 'users-paged-limit'), body: null },
    'users-get':    { method: 'GET',    path: () => `/users/${v('users-get-id')}`, body: null },
    'users-create': { method: 'POST',   path: () => '/users',                   body: () => ({ name: v('users-create-name'), email: v('users-create-email') }) },
    'users-patch':  { method: 'PATCH',  path: () => `/users/${v('users-patch-id')}`,  body: () => compact({ name: v('users-patch-name'), email: v('users-patch-email') }) },
    'users-delete': { method: 'DELETE', path: () => `/users/${v('users-delete-id')}`, body: null },

    'items-list':   { method: 'GET',    path: () => '/items',                   body: null },
    'items-paged':  { method: 'GET',    path: () => buildPaged('/items/paged', 'items-paged-skip', 'items-paged-limit'), body: null },
    'items-get':    { method: 'GET',    path: () => `/items/${v('items-get-id')}`, body: null },
    'items-user':   { method: 'GET',    path: () => `/items/user/${v('items-user-id')}`, body: null },
    'items-create': { method: 'POST',   path: () => '/items',                   body: () => compact({ title: v('items-create-title'), description: v('items-create-description'), user_id: num('items-create-user_id') }) },
    'items-patch':  { method: 'PATCH',  path: () => `/items/${v('items-patch-id')}`,  body: () => compact({ title: v('items-patch-title'), description: v('items-patch-description'), user_id: num('items-patch-user_id') }) },
    'items-delete': { method: 'DELETE', path: () => `/items/${v('items-delete-id')}`, body: null },
  };

  // ── メソッドカラー定義 ──────────────────────────────
  const METHOD_COLOR = {
    GET: 'method-get', POST: 'method-post',
    PATCH: 'method-patch', DELETE: 'method-delete'
  };

  // ── ヘルパー ────────────────────────────────────────
  function v(id) {
    const el = document.getElementById(id);
    return el ? el.value.trim() : '';
  }

  function num(id) {
    const val = v(id);
    return val ? parseInt(val, 10) : undefined;
  }

  /** ページネーション用クエリストリング生成 */
  function buildPaged(basePath, skipId, limitId) {
    const params = new URLSearchParams();
    const skip  = v(skipId);
    const limit = v(limitId);
    if (skip  !== '') params.set('skip',  skip);
    if (limit !== '') params.set('limit', limit);
    const qs = params.toString();
    return qs ? `${basePath}?${qs}` : basePath;
  }

  /** undefined / null / '' のキーを除去 */
  function compact(obj) {
    return Object.fromEntries(
      Object.entries(obj).filter(([, val]) => val !== undefined && val !== null && val !== '')
    );
  }

  function baseUrl() {
    return (document.getElementById('baseUrl').value || 'http://localhost:8000').replace(/\/$/, '');
  }

  function now() {
    return new Date().toLocaleTimeString('ja-JP', { hour12: false });
  }

  // ── タブ切り替え ────────────────────────────────────
  function switchTab(tab) {
    currentTab = tab;

    // nav ボタン
    document.querySelectorAll('.nav-btn').forEach(btn => {
      btn.classList.toggle('active', btn.dataset.tab === tab);
    });

    // コンテンツ
    document.querySelectorAll('.tab-content').forEach(el => {
      el.classList.toggle('active', el.id === `tab-${tab}`);
    });

    // ヘッダー更新
    const ep = ENDPOINTS[tab];
    if (ep) {
      const methodEl = document.getElementById('currentMethod');
      methodEl.textContent = ep.method;
      methodEl.className = `method-badge ${METHOD_COLOR[ep.method] || ''}`;

      // パスはプレビュー（IDなど未入力時はプレースホルダー表示）
      const rawPath = ep.path().replace('/undefined', '/:id').replace('NaN', ':id');
      document.getElementById('currentPath').textContent = rawPath;
    }
  }

  // ── リクエスト送信 ──────────────────────────────────
  async function send() {
    const ep = ENDPOINTS[currentTab];
    if (!ep) return;

    const path = ep.path();
    if (path.includes('undefined') || path.includes('NaN')) {
      showError('IDを入力してください');
      return;
    }

    const url = baseUrl() + path;
    const method = ep.method;
    const bodyData = ep.body ? ep.body() : null;

    // ステータス: 送信中
    setStatus('sending', '送信中...');

    const opts = {
      method,
      headers: { 'Content-Type': 'application/json' },
    };
    if (bodyData && method !== 'GET' && method !== 'DELETE') {
      opts.body = JSON.stringify(bodyData);
    }

    const startTime = performance.now();

    try {
      addLog('→', method, url, bodyData);

      const res = await fetch(url, opts);
      const elapsed = Math.round(performance.now() - startTime);

      let data;
      const contentType = res.headers.get('content-type') || '';
      if (contentType.includes('application/json')) {
        data = await res.json();
      } else {
        data = await res.text();
      }

      const ok = res.ok;
      setStatus(ok ? 'ok' : 'error', `${res.status} ${res.statusText}`);
      showResponse(data, res.status, elapsed, ok);
      addLog('←', res.status, res.statusText, data, elapsed, ok);

    } catch (err) {
      setStatus('error', '接続失敗');
      showError(`接続エラー: ${err.message}\n\nFastAPIサーバーが起動しているか確認してください。\nCORSの設定も確認してください。`);
      addLog('✕', 'ERROR', err.message, null, null, false);
    }
  }

  // ── UI 更新 ─────────────────────────────────────────
  function setStatus(type, text) {
    const ind = document.getElementById('statusIndicator');
    ind.className = `status-indicator status-${type}`;
    ind.querySelector('.status-text').textContent = text;
  }

  function showResponse(data, status, elapsed, ok) {
    const el = document.getElementById('responseBody');
    const meta = document.getElementById('responseMeta');

    const statusClass = ok ? 'status-ok' : 'status-err';
    meta.innerHTML = `<span class="${statusClass}">${status}</span> <span class="elapsed">${elapsed}ms</span>`;

    const json = JSON.stringify(data, null, 2);
    el.innerHTML = `<pre class="${ok ? '' : 'error-pre'}">${escapeHtml(json)}</pre>`;
  }

  function showError(msg) {
    const el = document.getElementById('responseBody');
    document.getElementById('responseMeta').innerHTML = '<span class="status-err">ERROR</span>';
    el.innerHTML = `<pre class="error-pre">${escapeHtml(msg)}</pre>`;
  }

  function clearResponse() {
    document.getElementById('responseBody').innerHTML = '<span class="placeholder">レスポンスがここに表示されます</span>';
    document.getElementById('responseMeta').innerHTML = '';
    setStatus('idle', '待機中');
  }

  // ── ログ ────────────────────────────────────────────
  function addLog(dir, method, urlOrStatus, data, elapsed, ok) {
    const el = document.getElementById('logBody');
    const line = document.createElement('div');
    line.className = `log-line ${ok === false ? 'log-err' : ok === true ? 'log-ok' : 'log-info'}`;

    let summary = '';
    if (data && typeof data === 'object') {
      summary = JSON.stringify(data).substring(0, 80);
      if (summary.length === 80) summary += '…';
    } else if (data) {
      summary = String(data).substring(0, 80);
    }

    line.innerHTML = `
      <span class="log-time">${now()}</span>
      <span class="log-dir">${dir}</span>
      <span class="log-method">${method}</span>
      <span class="log-url">${escapeHtml(String(urlOrStatus))}</span>
      ${elapsed !== null && elapsed !== undefined ? `<span class="log-elapsed">${elapsed}ms</span>` : ''}
      ${summary ? `<span class="log-summary">${escapeHtml(summary)}</span>` : ''}
    `;
    el.appendChild(line);
    el.scrollTop = el.scrollHeight;
  }

  function clearLog() {
    document.getElementById('logBody').innerHTML = '';
  }

  function escapeHtml(str) {
    return String(str)
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;');
  }

  // ── 初期化 ──────────────────────────────────────────
  function init() {
    document.querySelectorAll('.nav-btn').forEach(btn => {
      btn.addEventListener('click', () => switchTab(btn.dataset.tab));
    });

    // Enterキーでも送信
    document.addEventListener('keydown', e => {
      if (e.key === 'Enter' && e.ctrlKey) send();
    });

    switchTab('users-list');
  }

  document.addEventListener('DOMContentLoaded', init);

  return { send, clearResponse, clearLog };

})();
