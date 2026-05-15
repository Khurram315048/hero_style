
function updateCartCount() {
  const counter = document.getElementById("cart-count");
  const countEl = document.getElementById("server-cart-count");
  if (counter && countEl) {
    const n = parseInt(countEl.value) || 0;
    counter.innerText = n > 0 ? n : '';
  }
}


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


function openSearch() {
  const overlay=document.getElementById('searchOverlay');
  if(!overlay) return;
  overlay.style.display='flex';
  document.body.style.overflow='hidden';
  setTimeout(()=>{
    const input=document.getElementById('searchInput');
    if(input){
      input.focus();
      if(input.value.trim().length>=2){
        triggerSearch(input.value.trim());
      }
    }
  }, 100);
}

function closeSearch(){
  const overlay=document.getElementById('searchOverlay');
  if(overlay) overlay.style.display='none';
  document.body.style.overflow='';
  removeSearchDropdown();
}


function triggerSearch(query){
  fetch('/products/search?q=' + encodeURIComponent(query) + '&format=json')
    .then(res => res.json())
    .then(data => showSearchDropdown(data, query))
    .catch(() => removeSearchDropdown());
}


function goToSearchResults(query){
  if(query && query.trim()){
    window.location.href='/products/all_products?q=' + encodeURIComponent(query.trim());
  }
}

function initSearch(){
  const input=document.getElementById('searchInput');
  if(!input) return;

  let debounceTimer=null;

  input.addEventListener('keydown',function (e){
    if(e.key === 'Escape'){
      closeSearch();
      return;
    }
    if(e.key === 'Enter'){
      e.preventDefault();
      const query=this.value.trim();
      if(query.length > 0){
        closeSearch();
        goToSearchResults(query);
      }
    }
  });

  input.addEventListener('input', function (){
    const query=this.value.trim();
    clearTimeout(debounceTimer);
    if(query.length < 2){
      removeSearchDropdown();
      return;
    }
    debounceTimer=setTimeout(() => triggerSearch(query), 250);
  });


  const overlay=document.getElementById('searchOverlay');
  if(overlay){
    overlay.addEventListener('click', function (e) {
      if(e.target === this) closeSearch();
    });
  }


  document.addEventListener('keydown', function (e) {
    if(e.key === 'Escape') closeSearch();
  });


  document.addEventListener('keydown', function (e) {
    if((e.ctrlKey || e.metaKey) && e.key === 'k'){
      e.preventDefault();
      openSearch();
    }
  });
}


function showSearchDropdown(products,query){
  removeSearchDropdown();

  const box=document.querySelector('.search-box');
  if(!box) return;

  const drop=document.createElement('div');
  drop.id='search-dropdown';
  drop.style.cssText = `
    position: absolute; top: calc(100% + 6px); left: 0; right: 0;
    background: #0f1f33;
    border: 1px solid rgba(201,168,76,0.2);
    border-radius: 12px;
    max-height: 420px; overflow-y: auto; z-index: 2100;
    box-shadow: 0 12px 40px rgba(0,0,0,0.45);
    scrollbar-width: thin;
    scrollbar-color: rgba(201,168,76,0.2) transparent;
  `;


  if(!products || products.length===0){
    const empty=document.createElement('div');
    empty.style.cssText = `
      padding: 28px 20px; text-align: center;
      color: rgba(255,255,255,0.4); font-size: 13px;
    `;
    empty.innerHTML = `
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"
           style="width:32px;height:32px;margin:0 auto 10px;display:block;opacity:0.3">
        <circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/>
      </svg>
      No results found for "<span style="color:#c9a84c">${escapeHtml(query)}</span>"
    `;
    drop.appendChild(empty);
    box.appendChild(drop);
    return;
  }
  let lastCategory=null;


  products.slice(0, 6).forEach((p, i) => {

    if(p.category_name && p.category_name !== lastCategory){
        lastCategory=p.category_name;
        const heading=document.createElement('div');
        heading.style.cssText = `
            padding: 8px 18px 4px;
            font-size: 10px;
            letter-spacing: 1.5px;
            text-transform: uppercase;
            color: rgba(201,168,76,0.6);
            font-weight: 600;
        `;
        heading.textContent = p.category_name;
        drop.appendChild(heading);
    }

    const price=p.sale_price || p.base_price;
    const item=document.createElement('a');
    item.href='/products/' + p.product_id;
    item.style.cssText = `
      display: flex; align-items: center; gap: 14px;
      padding: 12px 18px;
      color: rgba(255,255,255,0.85);
      text-decoration: none; font-size: 13px;
      border-bottom: 1px solid rgba(255,255,255,0.04);
      transition: background 0.15s ease;
      ${i === 0 ? 'border-radius: 12px 12px 0 0;' : ''}
    `;
    item.onmouseover = () => item.style.background = 'rgba(201,168,76,0.08)';
    item.onmouseout = () => item.style.background = 'transparent';


    const imgWrap=document.createElement('div');
    imgWrap.style.cssText = `
      width: 44px; height: 44px; border-radius: 8px;
      background: #1a2e45; overflow: hidden; flex-shrink: 0;
      display: flex; align-items: center; justify-content: center;
    `;
    if(p.image_url){
      const img=document.createElement('img');
      img.src=p.image_url;
      img.alt=p.alt_text || p.title;
      img.style.cssText='width:100%;height:100%;object-fit:cover;';
      img.onerror=function () {
        this.style.display = 'none';
        imgWrap.innerHTML = `<svg viewBox="0 0 24 24" fill="none" stroke="rgba(201,168,76,0.3)" stroke-width="1.5" style="width:18px;height:18px"><circle cx="12" cy="12" r="9"/><circle cx="12" cy="12" r="2"/></svg>`;
      };
      imgWrap.appendChild(img);
    } 
    else{
      imgWrap.innerHTML=`<svg viewBox="0 0 24 24" fill="none" stroke="rgba(201,168,76,0.3)" stroke-width="1.5" style="width:18px;height:18px"><circle cx="12" cy="12" r="9"/><circle cx="12" cy="12" r="2"/></svg>`;
    }


    const info=document.createElement('div');
    info.style.cssText = 'flex:1; min-width:0;';

    const titleEl=document.createElement('div');
    titleEl.style.cssText = 'font-weight:500; color:#fff; white-space:nowrap; overflow:hidden; text-overflow:ellipsis;';
    titleEl.textContent=p.title;

    const meta=document.createElement('div');
    meta.style.cssText = 'display:flex; align-items:center; gap:8px; margin-top:3px;';

    const priceEl=document.createElement('span');
    priceEl.style.cssText = 'color:rgba(201,168,76,0.85); font-size:12px; font-weight:500;';
    priceEl.textContent='PKR ' + Number(price).toLocaleString();
    meta.appendChild(priceEl);

    if(p.category_name){
      const cat=document.createElement('span');
      cat.style.cssText = `
        font-size:10px; color:rgba(255,255,255,0.35);
        background:rgba(255,255,255,0.06); padding:2px 7px;
        border-radius:10px; letter-spacing:0.5px;
      `;
      cat.textContent=p.category_name;
      meta.appendChild(cat);
    }

    info.appendChild(titleEl);
    info.appendChild(meta);

    const arrow = document.createElement('div');
    arrow.style.cssText = 'flex-shrink:0; color:rgba(255,255,255,0.15); transition:color 0.15s;';
    arrow.innerHTML = `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="width:14px;height:14px"><polyline points="9 18 15 12 9 6"/></svg>`;
    item.onmouseover = () => { item.style.background = 'rgba(201,168,76,0.08)'; arrow.style.color = 'rgba(201,168,76,0.6)'; };
    item.onmouseout = () => { item.style.background = 'transparent'; arrow.style.color = 'rgba(255,255,255,0.15)'; };

    item.appendChild(imgWrap);
    item.appendChild(info);
    item.appendChild(arrow);
    drop.appendChild(item);
  });


  const footer=document.createElement('a');
  footer.href='/products/search?q='+encodeURIComponent(query);
  footer.style.cssText= `
    display: flex; align-items: center; justify-content: center; gap: 6px;
    padding: 13px 18px;
    color: #c9a84c; font-size: 12px; font-weight: 500;
    letter-spacing: 1px; text-transform: uppercase;
    text-decoration: none;
    border-top: 1px solid rgba(201,168,76,0.12);
    border-radius: 0 0 12px 12px;
    transition: background 0.15s;
  `;
  footer.innerHTML = `
    See all results for "${escapeHtml(query)}"
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" style="width:12px;height:12px"><line x1="5" y1="12" x2="19" y2="12"/><polyline points="12 5 19 12 12 19"/></svg>
  `;
  footer.onmouseover = () => footer.style.background = 'rgba(201,168,76,0.06)';
  footer.onmouseout = () => footer.style.background = 'transparent';
  drop.appendChild(footer);

  box.appendChild(drop);
}


function removeSearchDropdown(){
  const d=document.getElementById('search-dropdown');
  if(d) d.remove();
}


function escapeHtml(str){
  const div=document.createElement('div');
  div.textContent=str;
  return div.innerHTML;
}


function updateQuantity(delta){
  const qtyInput=document.getElementById('quantity');
  if(!qtyInput) return;
  const next=Math.max(1, Math.min(10, parseInt(qtyInput.value) + delta));
  qtyInput.value = next;
}


function showTab(tab){
  document.querySelectorAll('.tab-pane').forEach(x => x.classList.remove('active'));
  document.querySelectorAll('.tab-btn').forEach(x => x.classList.remove('active'));
  document.getElementById(tab).classList.add('active');
  event.target.classList.add('active');
}


document.addEventListener("DOMContentLoaded", () => {
  updateCartCount();
  initSearch();
});



function initSelectAll(selectAllId, checkboxName, tableBodyId) {
    const selectAll = document.getElementById(selectAllId);
    if (!selectAll) return;

    const tableBody = document.getElementById(tableBodyId);

    selectAll.addEventListener('change', function () {
        tableBody.querySelectorAll(`input[name="${checkboxName}"]`)
                 .forEach(cb => cb.checked = this.checked);
    });
    tableBody.addEventListener('change', function (e) {
        if (e.target.name !== checkboxName) return;
        const all     = tableBody.querySelectorAll(`input[name="${checkboxName}"]`);
        const checked = tableBody.querySelectorAll(`input[name="${checkboxName}"]:checked`);
        selectAll.checked = all.length === checked.length;
    });
}