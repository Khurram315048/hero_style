// ─── Cart Count (reads from server via hidden element) ────
function updateCartCount() {
  const counter = document.getElementById("cart-count");
  const countEl = document.getElementById("server-cart-count");
  if (counter && countEl) {
    const n = parseInt(countEl.value) || 0;
    counter.innerText = n > 0 ? n : '';
  }
}

// ─── Toast notification ───────────────────────────────────
function showCartToast(title) {
  let existing = document.getElementById('cart-toast');
  if (existing) existing.remove();

  let toast = document.createElement('div');
  toast.id = 'cart-toast';
  toast.style.cssText = `
    position: fixed; bottom: 24px; right: 24px;
    background: #0d1b2a; color: #c9a84c;
    border: 1px solid rgba(201,168,76,0.35);
    border-radius: 8px; padding: 12px 20px;
    font-size: 13px; font-weight: 500;
    box-shadow: 0 8px 24px rgba(0,0,0,0.3);
    z-index: 9999; opacity: 0;
    transition: opacity 0.3s ease;
    max-width: 280px;
  `;
  toast.textContent = '✓  Added to cart: ' + title;
  document.body.appendChild(toast);
  setTimeout(() => toast.style.opacity = '1', 10);
  setTimeout(() => {
    toast.style.opacity = '0';
    setTimeout(() => toast.remove(), 300);
  }, 2500);
}

// ─── Search: Open / Close ─────────────────────────────────
function openSearch() {
  const overlay = document.getElementById('searchOverlay');
  if (overlay) {
    overlay.classList.add('active');
    setTimeout(() => {
      const input = document.getElementById('searchInput');
      if (input) input.focus();
    }, 100);
  }
}

function closeSearch() {
  const overlay = document.getElementById('searchOverlay');
  if (overlay) overlay.classList.remove('active');
  removeSearchDropdown();
}

function initSearch() {
  const input = document.getElementById('searchInput');
  if (!input) return;

  input.addEventListener('keydown', function(e) {
    if (e.key === 'Enter') {
      const query = this.value.trim();
      if (query) window.location.href = '/search?q=' + encodeURIComponent(query);
    }
    if (e.key === 'Escape') closeSearch();
  });

  input.addEventListener('input', function() {
    const query = this.value.trim();
    if (query.length < 2) { removeSearchDropdown(); return; }
    fetch('/search?q=' + encodeURIComponent(query) + '&format=json')
      .then(res => res.json())
      .then(data => showSearchDropdown(data, query))
      .catch(() => removeSearchDropdown());
  });

  document.addEventListener('click', function(e) {
    if (!e.target.closest('.search-box')) removeSearchDropdown();
  });

  const overlay = document.getElementById('searchOverlay');
  if (overlay) {
    overlay.addEventListener('click', function(e) {
      if (e.target === this) closeSearch();
    });
  }

  document.addEventListener('keydown', function(e) {
    if (e.key === 'Escape') closeSearch();
  });
}

function showSearchDropdown(products, query) {
  removeSearchDropdown();
  if (!products.length) return;
  const box = document.querySelector('.search-box');
  if (!box) return;

  const drop = document.createElement('div');
  drop.id = 'search-dropdown';
  drop.style.cssText = `
    position: absolute; top: 100%; left: 0; right: 0;
    background: #0d1b2a;
    border: 1px solid rgba(201,168,76,0.2);
    border-top: none; border-radius: 0 0 8px 8px;
    max-height: 320px; overflow-y: auto; z-index: 1200;
  `;

  products.slice(0, 6).forEach(p => {
    const item = document.createElement('a');
    item.href = '/products/' + p.product_id;
    item.style.cssText = `
      display:flex; align-items:center; gap:12px;
      padding:10px 16px; color:rgba(255,255,255,0.85);
      text-decoration:none; font-size:13px;
      border-bottom:1px solid rgba(255,255,255,0.05);
      transition:background 0.2s;
    `;
    item.onmouseover = () => item.style.background = 'rgba(201,168,76,0.1)';
    item.onmouseout  = () => item.style.background = 'transparent';
    item.innerHTML = `
      <img src="${p.image_url || ''}" style="width:36px;height:36px;object-fit:cover;border-radius:4px;background:#1a2e45;flex-shrink:0;" onerror="this.style.display='none'"/>
      <div>
        <div style="font-weight:500;">${p.title}</div>
        <div style="color:rgba(201,168,76,0.7);font-size:11px;">PKR ${Number(p.sale_price || p.base_price).toLocaleString()}</div>
      </div>
    `;
    drop.appendChild(item);
  });

  const seeAll = document.createElement('a');
  seeAll.href = '/search?q=' + encodeURIComponent(query);
  seeAll.style.cssText = `display:block; text-align:center; padding:10px; color:#c9a84c; font-size:12px; letter-spacing:1px; text-transform:uppercase; text-decoration:none;`;
  seeAll.textContent = 'See all results →';
  drop.appendChild(seeAll);

  box.style.position = 'relative';
  box.appendChild(drop);
}

function removeSearchDropdown() {
  const d = document.getElementById('search-dropdown');
  if (d) d.remove();
}

// ─── Checkout: quantity controls on product page ──────────
function updateQuantity(delta) {
  const qtyInput = document.getElementById('quantity');
  if (!qtyInput) return;
  const next = Math.max(1, Math.min(10, parseInt(qtyInput.value) + delta));
  qtyInput.value = next;
}

function showTab(tab) {
  document.querySelectorAll('.tab-pane').forEach(x => x.classList.remove('active'));
  document.querySelectorAll('.tab-btn').forEach(x => x.classList.remove('active'));
  document.getElementById(tab).classList.add('active');
  event.target.classList.add('active');
}

// ─── Init ─────────────────────────────────────────────────
document.addEventListener("DOMContentLoaded", () => {
  updateCartCount();
  initSearch();
});