// ─── Cart Count ────────────────────────────────────────────
function updateCartCount() {
  const counter = document.getElementById("cart-count");
  const countEl = document.getElementById("server-cart-count");
  if (counter && countEl) {
    const n = parseInt(countEl.value) || 0;
    counter.innerText = n > 0 ? n : '';
  }
}

// ─── Cart Toast ────────────────────────────────────────────
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
  toast.textContent = title;
  document.body.appendChild(toast);
  setTimeout(() => toast.style.opacity = '1', 10);
  setTimeout(() => {
    toast.style.opacity = '0';
    setTimeout(() => toast.remove(), 300);
  }, 2500);
}

// ─── Search Open/Close ─────────────────────────────────────
function openSearch() {
  const overlay = document.getElementById('searchOverlay');
  if (!overlay) return;
  overlay.style.display = 'flex';
  setTimeout(() => {
    const input = document.getElementById('searchInput');
    if (input) {
      input.focus();
      if (input.value.trim().length >= 2) {
        triggerSearch(input.value.trim());
      }
    }
  }, 100);
}

function closeSearch() {
  const overlay = document.getElementById('searchOverlay');
  if (overlay) overlay.style.display = 'none';
  removeSearchDropdown();
}

// ─── Core Search Fetch ─────────────────────────────────────
function triggerSearch(query) {
  fetch('/search?q=' + encodeURIComponent(query) + '&format=json')
    .then(res => res.json())
    .then(data => showSearchDropdown(data, query))
    .catch(() => removeSearchDropdown());
}

// ─── Search Init ───────────────────────────────────────────
function initSearch() {
  const input = document.getElementById('searchInput');
  if (!input) return;

  let debounceTimer = null;

  input.addEventListener('keydown', function(e) {
    if (e.key === 'Escape') {
      closeSearch();
      return;
    }
    if (e.key === 'Enter') {
      const firstLink = document.querySelector('#search-dropdown a[href^="/products/"]');
      if (firstLink) window.location.href = firstLink.href;
    }
  });

  input.addEventListener('input', function() {
    const query = this.value.trim();
    clearTimeout(debounceTimer);
    if (query.length < 2) {
      removeSearchDropdown();
      return;
    }
    debounceTimer = setTimeout(() => triggerSearch(query), 300);
  });

  const overlay = document.getElementById('searchOverlay');
  if (overlay) {
    overlay.addEventListener('click', function(e) {
      if (e.target === this) closeSearch();
    });
  }

  document.addEventListener('click', function(e) {
    if (!e.target.closest('#searchOverlay')) removeSearchDropdown();
  });

  document.addEventListener('keydown', function(e) {
    if (e.key === 'Escape') closeSearch();
  });
}

// ─── Dropdown Show ─────────────────────────────────────────
function showSearchDropdown(products, query) {
  removeSearchDropdown();

  const overlay = document.getElementById('searchOverlay');
  const box = overlay ? overlay.querySelector('.search-box') : null;
  if (!box) return;

  const drop = document.createElement('div');
  drop.id = 'search-dropdown';
  drop.style.cssText = `
    position: absolute; top: 100%; left: 0; right: 0;
    background: #0d1b2a;
    border: 1px solid rgba(201,168,76,0.2);
    border-top: none; border-radius: 0 0 8px 8px;
    max-height: 360px; overflow-y: auto; z-index: 1200;
  `;

  // Koi result nahi
  if (!products || products.length === 0) {
    drop.style.padding = '16px';
    drop.style.textAlign = 'center';
    drop.style.color = 'rgba(255,255,255,0.4)';
    drop.style.fontSize = '13px';
    drop.textContent = '"' + query + '" ka koi nateeja nahi mila';
    box.style.position = 'relative';
    box.appendChild(drop);
    return;
  }

  products.slice(0, 7).forEach(p => {
    const price = p.sale_price || p.base_price;
    const item = document.createElement('a');
    item.href = '/products/' + p.product_id;
    item.style.cssText = `
      display: flex; align-items: center; gap: 12px;
      padding: 10px 16px;
      color: rgba(255,255,255,0.85);
      text-decoration: none; font-size: 13px;
      border-bottom: 1px solid rgba(255,255,255,0.05);
      transition: background 0.15s;
    `;
    item.onmouseover = () => item.style.background = 'rgba(201,168,76,0.08)';
    item.onmouseout  = () => item.style.background = 'transparent';

    const img = document.createElement('img');
    img.src = p.image_url || '';
    img.style.cssText = 'width:40px;height:40px;object-fit:cover;border-radius:6px;background:#1a2e45;flex-shrink:0;';
    img.onerror = function() { this.style.display = 'none'; };

    const info = document.createElement('div');
    info.style.flex = '1';
    info.innerHTML = `
      <div style="font-weight:500;color:#fff;">${p.title}</div>
      <div style="color:rgba(201,168,76,0.8);font-size:11px;margin-top:2px;">
        PKR ${Number(price).toLocaleString()}
      </div>
    `;

    item.appendChild(img);
    item.appendChild(info);
    drop.appendChild(item);
  });

  // Sab results dekhne ka link
  const seeAll = document.createElement('a');
  seeAll.href = '/search?q=' + encodeURIComponent(query);
  seeAll.style.cssText = `
    display: block; text-align: center; padding: 10px 16px;
    color: #c9a84c; font-size: 12px; letter-spacing: 1px;
    text-transform: uppercase; text-decoration: none;
    border-top: 1px solid rgba(201,168,76,0.15);
    transition: background 0.15s;
  `;
  seeAll.textContent = 'Tamam results dekhein →';
  seeAll.onmouseover = () => seeAll.style.background = 'rgba(201,168,76,0.06)';
  seeAll.onmouseout  = () => seeAll.style.background = 'transparent';
  drop.appendChild(seeAll);

  box.style.position = 'relative';
  box.appendChild(drop);
}

// ─── Dropdown Remove ───────────────────────────────────────
function removeSearchDropdown() {
  const d = document.getElementById('search-dropdown');
  if (d) d.remove();
}

// ─── Product Page Quantity ─────────────────────────────────
function updateQuantity(delta) {
  const qtyInput = document.getElementById('quantity');
  if (!qtyInput) return;
  const next = Math.max(1, Math.min(10, parseInt(qtyInput.value) + delta));
  qtyInput.value = next;
}

// ─── Tabs ──────────────────────────────────────────────────
function showTab(tab) {
  document.querySelectorAll('.tab-pane').forEach(x => x.classList.remove('active'));
  document.querySelectorAll('.tab-btn').forEach(x => x.classList.remove('active'));
  document.getElementById(tab).classList.add('active');
  event.target.classList.add('active');
}

// ─── Init ──────────────────────────────────────────────────
document.addEventListener("DOMContentLoaded", () => {
  updateCartCount();
  initSearch();
});