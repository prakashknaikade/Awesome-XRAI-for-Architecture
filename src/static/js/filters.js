/*
   Filtering + Ordered Tag Rendering + Active Filters + Clear-All Reset
*/

(function(){

/* ------------------ Shared State ------------------ */
const ST = window.state || (window.state = {
  includeTags: new Set(),
  excludeTags: new Set(),
  selectedPapers: new Set(),
  onlyShowSelected: false
});

/* ------------------ Selected-only helpers ------------------ */
function setSelectedOnlyButtonUI() {
  const btn = document.querySelector('.selected-only-mode-toggle');
  if (!btn) return;
  btn.classList.toggle('active', !!ST.onlyShowSelected);
  btn.setAttribute('aria-pressed', ST.onlyShowSelected ? 'true' : 'false');
  btn.title = ST.onlyShowSelected ? 'Showing selected papers only' : 'Show Selected Only';
}

function syncSelectedPapersFromDom() {
  const checkedIds = new Set();
  document.querySelectorAll('.paper-row .selection-checkbox:checked').forEach(cb => {
    const row = cb.closest('.paper-row');
    const id = row && row.getAttribute('data-id');
    if (id) checkedIds.add(id);
  });

  ST.selectedPapers.clear();
  checkedIds.forEach(id => ST.selectedPapers.add(id));
}

function toggleSelectedOnly(forceValue) {
  if (typeof forceValue === 'boolean') {
    ST.onlyShowSelected = forceValue;
  } else {
    ST.onlyShowSelected = !ST.onlyShowSelected;
  }
  setSelectedOnlyButtonUI();
  applyFilters();
}
window.toggleSelectedOnly = toggleSelectedOnly;

/* ------------------ Search box helpers ------------------ */
function clearSearch() {
  const input = document.getElementById('searchInput');
  if (!input) return;

  // Clear value
  input.value = '';

  // Hide the X
  const btn = input.parentElement && input.parentElement.querySelector('.clear-search-btn');
  if (btn) btn.style.visibility = 'hidden';

  // Trigger the same pipeline as typing (fires applyFilters and rebuilds chips)
  input.dispatchEvent(new Event('input', { bubbles: true }));

  // Focus back for convenience
  input.focus();
}
window.clearSearch = clearSearch;

function wireSearchBox() {
  const input = document.getElementById('searchInput');
  if (!input) return;
  const btn = input.parentElement && input.parentElement.querySelector('.clear-search-btn');

  const updateBtn = () => {
    if (!btn) return;
    btn.style.visibility = input.value ? 'visible' : 'hidden';
  };

  // Initial state
  updateBtn();

  // Typing triggers filtering and button visibility
  input.addEventListener('input', () => {
    updateBtn();
    if (typeof window.applyFilters === 'function') window.applyFilters();
  });

  // ESC to clear
  input.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
      e.preventDefault();
      clearSearch();
    }
  });

  // Also clear on click (works even if inline onclick is removed later)
  if (btn && !btn.__wired) {
    btn.addEventListener('click', (e) => { e.preventDefault(); clearSearch(); });
    btn.__wired = true;
  }
}

// Focus search box (for floating nav button)
function focusSearchBox() {
  const input = document.getElementById('searchInput');
  if (!input) return;
  input.focus({ preventScroll: false });
  const val = input.value;
  try {
    input.setSelectionRange(val.length, val.length);
  } catch (_) {}
}
window.focusSearchBox = focusSearchBox;

// Wire on load (safe even if other init runs too)
document.addEventListener('DOMContentLoaded', wireSearchBox);

/* ------------------ Master Tag Ordering ------------------ */
const MASTER_TAG_ORDER = [
  "Generative Design and Design Space Exploration",
  "geometry generation", "Form Finding","design automation","GANs","VAE",
  "diffusion models","RL","procedural modeling","text-to-3D","image-to-3D","conditional generation",
  "design space optimization","multi-objective optimization","search-based design",
  
  "Parametric, Computational and Algorithmic Design",
  "rule-based modeling","structural optimization","Grasshopper","Rhino","Houdini",

  "Performance-Driven Design",
  "energy modeling","energy optimization","thermal simulation","daylight optimization",
  "acoustics","structural efficiency","AI performance feedback",
  "environmental simulation","multi-criteria optimization",

  "3D Reconstruction",
  "point clouds","LiDAR","photogrammetry","SLAM","NeRF","3DGS","SfM",
  "indoor scene reconstruction","outdoor scene reconstruction","scene understanding",
  "scene editing","scene interaction",

  "Floor Plan Reconstruction and Parametrization",
  "digital twins","BIM","parametric BIM","mesh-to-BIM","scan-to-BIM","point-cloud-to-plan","image-to-plan",
  "2D floor plan","3D floor plan","layout recovery","room segmentation",
  "object detection","semantic segmentation","structural element detection","Revit automation",

  "Predictive Analytics and Performance Optimization",
  "predictive analytics","building energy forecasting",
  "time-series analysis","anomaly detection",

  "Quality Control and Validation",
  "BIM validation","model checking","clash detection","data quality","geometric validation",
  "automated compliance checking","QA/QC in BIM",

  "Digital Documentation and Archiving",
  "heritage digitization","digital archives","3D scanning",
  "Heritage BIM","documentation workflows",

  "Predictive Conservation and Risk Assessment",
  "conservation AI","risk assessment","risk modeling","structural health monitoring","predictive maintenance",
  "damage detection","material degradation prediction",

  "Virtual Reality Experiences and Education",
  "cultural heritage VR", "museum VR", "AR cultural experiences",
  "heritage XR visualization", "immersive education", "XR storytelling",

  "AI for Energy Performance Optimization",
  "building energy simulation","AI HVAC optimization",
  "energy-efficient design","smart grids",

  "Sustainable Buildings",
  "lifecycle assessment","sustainable materials","embodied carbon","material simulation",
  "AI material selection","circular economy","material passports",
  "sustainable construction","sustainable disassembly",

  "Smart Building Systems and IoT Integration",
  "intelligent environments","AI building automation","adaptive control","real-time monitoring",
  "human-centric IoT","sensor data integration","building performance dashboard",
  "big data in buildings","blockchain for AEC", "data templates for circularity",

  "AI-Powered Real Estate Valuation",
  "predictive pricing","ML for sustainable real estate",
  "AI in asset management","real estate analytics","predictive investment",
  "asset performance",

  "Virtual Property Tours and Marketing",
  "XR immersive walkthroughs", "real estate visualization", "virtual staging",

  "XRAI for AEC",
  "immersive design", "collaborative VR co-design", "XR design review",  
  "XRAI inclusive design", "XRAI automated accessibility",
  "AR/VR/XR visualization", "Interactive Visualization",
  "AR/VR interfaces", "VR dashboards", "adaptive environments", "metaverse for AEC",
  "Unity", "Unreal Engine",

  "Occupant Behavior Analysis and Spatial Optimization",
  "HCI-HBI", "occupant behavior", "spatial analytics", "movement analysis", "space utilization",
  "sensor-driven design", "AI occupancy modeling", "behavior modeling",

  "Cross-Modal Intelligence and Multimodal Integration",
  "Vision-Language Models for AEC","LLMs for AEC","Multimodal Design Assistance",
  "Context-Aware Spatial Intelligence", "Agent-based Modeling",
  
  "Review Paper","Dataset", "Case Study", "Tool/Library",
];
const MASTER_INDEX = MASTER_TAG_ORDER.reduce((m,t,i)=>{m[t]=i;return m;}, {});

/* ------------------ Helpers ------------------ */
function normalizeCategory(c){
  return (c||'Uncategorized').trim().replace(/\s+/g,' ').toLowerCase();
}

function isHighlightedTag(tag){
  const set = window.HIGHLIGHTED_TAGS;
  if (!set) return false;
  if (set.has(tag)) return true;
  const norm = tag.replace(/&/g,'and');
  for (const h of set){
    if (h.replace(/&/g,'and') === norm) return true;
  }
  return false;
}

/* ------------------ Index Builder ------------------ */
function buildIndex(){
  const rows = Array.from(document.querySelectorAll('.paper-row'));
  const map = { all: new Set() };
  const yearsMap = { all: new Set() };            // NEW

  rows.forEach(r=>{
    const cat = normalizeCategory(r.getAttribute('data-primary-category'));
    r.dataset.primaryKey = cat;
    if(!map[cat]) map[cat]=new Set();
    if(!yearsMap[cat]) yearsMap[cat]=new Set();

    let tags=[];
    try { tags = JSON.parse(r.getAttribute('data-tags')||'[]'); } catch {}
    tags.forEach(t=>{
      map.all.add(t);
      map[cat].add(t);
    });

    const y = r.getAttribute('data-year');
    if (y) { yearsMap.all.add(y); yearsMap[cat].add(y); } // NEW
  });

  const lists={};
  Object.keys(map).forEach(k=>{
    lists[k]=Array.from(map[k]).sort((a,b)=>a.localeCompare(b));
  });

  const yearLists={};                                 // NEW
  Object.keys(yearsMap).forEach(k=>{
    yearLists[k]=Array.from(yearsMap[k]).sort((a,b)=>parseInt(b)-parseInt(a));
  });

  return { rows, categoryTags: lists, categoryYears: yearLists }; // NEW
}

/* ------------------ Tag Ordering ------------------ */
function orderedTagsSubset(tags){
  const s = new Set(tags);
  const primary = MASTER_TAG_ORDER.filter(t=>s.has(t));
  if (primary.length === tags.length) return primary;
  const leftovers = tags.filter(t=>!(t in MASTER_INDEX)).sort((a,b)=>a.localeCompare(b));
  return [...primary, ...leftovers];
}

/* ------------------ Tag Bar ------------------ */
function renderTagBar(catKey){
  const el = document.getElementById('tagFilters');
  if (!el) return;

  // FIX: normalize key so it matches the index built with normalizeCategory()
  const scopeKey = (!catKey || catKey === 'all') ? 'all' : normalizeCategory(catKey);

  const tags = (window.__FILTER_INDEX?.categoryTags?.[scopeKey]) || [];
  const ordered = orderedTagsSubset(tags);
  el.innerHTML = '';
  ordered.forEach(tag=>{
    const pill = document.createElement('div');
    pill.className = 'tag-filter';
    pill.dataset.tag = tag;
    pill.textContent = tag;
    if (isHighlightedTag(tag)) pill.classList.add('highlighted');
    if (ST.includeTags.has(tag)) pill.classList.add('include');
    else if (ST.excludeTags.has(tag)) pill.classList.add('exclude');
    pill.addEventListener('click', ()=>{
      if (!pill.classList.contains('include') && !pill.classList.contains('exclude')){
        pill.classList.add('include'); ST.includeTags.add(tag);
      } else if (pill.classList.contains('include')){
        pill.classList.remove('include'); pill.classList.add('exclude');
        ST.includeTags.delete(tag); ST.excludeTags.add(tag);
      } else {
        pill.classList.remove('exclude');
        ST.excludeTags.delete(tag);
      }
      applyFilters();
    });
    el.appendChild(pill);
  });

  // Purge selections outside scope
  ST.includeTags.forEach(t=>{ if(!tags.includes(t)) ST.includeTags.delete(t); });
  ST.excludeTags.forEach(t=>{ if(!tags.includes(t)) ST.excludeTags.delete(t); });
}

function syncTagPillsFromState(){
  const el = document.getElementById('tagFilters');
  if (!el) return;
  el.querySelectorAll('.tag-filter').forEach(p=>{
    const t = p.dataset.tag;
    p.classList.remove('include','exclude');
    if (ST.includeTags.has(t)) p.classList.add('include');
    else if (ST.excludeTags.has(t)) p.classList.add('exclude');
  });
}

/* ------------------ Active Filters UI ------------------ */
function buildActiveFilters(){
  const box = document.getElementById('activeFilters');
  if (!box) return;
  box.innerHTML = '';

  const categoryEl = document.getElementById('categoryFilter');
  const yearEl = document.getElementById('yearFilter');
  const searchEl = document.getElementById('searchInput');

  const chips = [];

  if (categoryEl && categoryEl.value && categoryEl.value !== 'all')
    chips.push(makeChip('Category', categoryEl.value,'category'));
  if (yearEl && yearEl.value && yearEl.value !== 'all')
    chips.push(makeChip('Year', yearEl.value,'year'));
  if (searchEl && searchEl.value.trim())
    chips.push(makeChip('Search', searchEl.value.trim(),'search'));

  [...ST.includeTags].sort().forEach(t=>chips.push(makeChip('Include', t, 'include-tag', t)));
  [...ST.excludeTags].sort().forEach(t=>chips.push(makeChip('Exclude', t, 'exclude-tag', t)));

  if (!chips.length){
    const span = document.createElement('span');
    span.className = 'no-active-filters';
    span.textContent = 'No active filters';
    box.appendChild(span);
  } else {
    chips.forEach(c=>box.appendChild(c));
  }
}

function makeChip(label,value,type,dataValue){
  const chip = document.createElement('button');
  chip.className = 'active-filter-chip';
  chip.dataset.type = type;
  if (dataValue) chip.dataset.value = dataValue;
  chip.innerHTML = `<strong>${label}:</strong> ${value} <span class="x">×</span>`;
  chip.addEventListener('click', ()=>removeFilter(type,value));
  return chip;
}

function removeFilter(type,value){
  if (type==='category'){
    const el=document.getElementById('categoryFilter');
    if (el){ el.value='all'; renderTagBar('all'); }
  } else if (type==='year'){
    const el=document.getElementById('yearFilter'); if (el) el.value='all';
  } else if (type==='search'){
    const el=document.getElementById('searchInput'); if (el) el.value='';
  } else if (type==='include-tag'){
    ST.includeTags.delete(value);
  } else if (type==='exclude-tag'){
    ST.excludeTags.delete(value);
  }
  syncTagPillsFromState();
  applyFilters();
}

/* ------------------ Counts & Numbering ------------------ */
function updatePaperNumbers(){
  const rows = window.__FILTER_INDEX.rows;
  const total = rows.length;
  let visible = 0, seq = 1;
  rows.forEach(r=>{
    const show = r.classList.contains('visible');
    const numEl = r.querySelector('.paper-number');
    if (show){
      visible++;
      if (numEl) numEl.textContent = seq++;
    } else if (numEl){
      numEl.textContent = '';
    }
  });
  const visEl = document.getElementById('visibleCount');
  const totEl = document.getElementById('totalCount');
  if (visEl) visEl.textContent = visible;
  if (totEl) totEl.textContent = total;
}

/* ------------------ Year dropdown helpers (ADD) ------------------ */
function setYearOptions(years){
  const el = document.getElementById('yearFilter');
  if (!el) return;
  const prev = el.value || 'all';
  const list = Array.from(new Set(years || [])).sort((a,b)=>parseInt(b)-parseInt(a));
  el.innerHTML = '';
  const optAll = document.createElement('option');
  optAll.value = 'all'; optAll.textContent = 'All Years';
  el.appendChild(optAll);
  list.forEach(y=>{
    const o = document.createElement('option');
    o.value = y; o.textContent = y;
    el.appendChild(o);
  });
  el.value = (prev === 'all' || list.includes(prev)) ? prev : 'all';
}

function setYearOptionsAll(){
  const idx = window.__FILTER_INDEX;
  if (!idx) return;
  setYearOptions(idx.categoryYears?.all || []);
}

function setYearOptionsFromVisible(){
  const years = new Set();
  (window.__FILTER_INDEX?.rows || []).forEach(r=>{
    if (r.classList.contains('visible')){
      const y = r.getAttribute('data-year');
      if (y) years.add(y);
    }
  });

  if (years.size > 0){
    setYearOptions(Array.from(years));
  } else {
    // fallback to current category scope
    const categoryEl = document.getElementById('categoryFilter');
    const key = normalizeCategory(categoryEl ? categoryEl.value : 'all');
    const list = window.__FILTER_INDEX?.categoryYears?.[key] || window.__FILTER_INDEX?.categoryYears?.all || [];
    setYearOptions(list);
  }
}

/* ------------------ Core Filtering ------------------ */
function applyFilters(){
  const searchEl = document.getElementById('searchInput');
  const yearEl = document.getElementById('yearFilter');
  const categoryEl = document.getElementById('categoryFilter');

  // Keep selected IDs synced with actual checkbox state
  syncSelectedPapersFromDom();

  const term = (searchEl && searchEl.value ? searchEl.value : '').toLowerCase();
  const yearVal = yearEl ? yearEl.value : 'all';
  const catKey = normalizeCategory(categoryEl ? categoryEl.value : 'all');
  const selectedOnly = !!ST.onlyShowSelected;

  window.__FILTER_INDEX.rows.forEach(r=>{
    const title = (r.getAttribute('data-title')||'').toLowerCase();
    const authors = (r.getAttribute('data-authors')||'').toLowerCase();
    const year = r.getAttribute('data-year')||'';
    const rowCat = r.dataset.primaryKey;
    const rowId = r.getAttribute('data-id');
    let tags=[];
    try { tags = JSON.parse(r.getAttribute('data-tags')||'[]'); } catch {}

    const passSearch = !term || title.includes(term) || authors.includes(term);
    const passYear   = (yearVal === 'all') || (year === yearVal);
    const passCat    = (catKey === 'all') || (rowCat === catKey);
    const passInclude= ST.includeTags.size===0 || [...ST.includeTags].every(t=>tags.includes(t));
    const passExclude= ST.excludeTags.size===0 || ![...ST.excludeTags].some(t=>tags.includes(t));

    // If selected-only mode is ON, show only selected papers (ignore other filters)
    const visible = selectedOnly
      ? !!(rowId && ST.selectedPapers.has(rowId))
      : (passSearch && passYear && passCat && passInclude && passExclude);

    r.classList.toggle('visible', visible);
  });

  updatePaperNumbers();
  buildActiveFilters();
  setYearOptionsFromVisible();               // keep years in sync with current scope
  if (typeof lazyLoadInstance !== 'undefined') lazyLoadInstance.update();
}

/* ------------------ FULL RESET (Exposed) ------------------ */
function resetAllFilters(){
  // Clear logical state
  ST.includeTags.clear();
  ST.excludeTags.clear();
  ST.onlyShowSelected = false;

  // Reset inputs
  const searchEl = document.getElementById('searchInput');
  const yearEl = document.getElementById('yearFilter');
  const categoryEl = document.getElementById('categoryFilter');

  if (searchEl) searchEl.value = '';
  if (yearEl) yearEl.value = 'all';
  if (categoryEl) categoryEl.value = 'all';

  // Re-render tag bar (neutral)
  renderTagBar('all');

  // Show all rows
  if (window.__FILTER_INDEX && window.__FILTER_INDEX.rows){
    window.__FILTER_INDEX.rows.forEach(r=>r.classList.add('visible'));
  }

  // Remove any include/exclude classes (safety)
  syncTagPillsFromState();

  // Rebuild chips & counts
  buildActiveFilters();
  updatePaperNumbers();
  setYearOptionsAll();                       // restore full year list
  setSelectedOnlyButtonUI();

  // Clear URL (fallback)
  if (history.replaceState){
    history.replaceState(null,'',location.pathname);
  }
}
window.resetAllFilters = resetAllFilters;

/* ------------------ Init ------------------ */
document.addEventListener('DOMContentLoaded', ()=>{
  window.__FILTER_INDEX = buildIndex();
  window.__FILTER_INDEX.rows.forEach(r=>r.classList.add('visible'));

  const categoryEl = document.getElementById('categoryFilter');
  if (categoryEl){
    [...categoryEl.options].forEach(opt=>{
      if (/^\s*All Categories\s*$/i.test(opt.textContent)) opt.value='all';
    });
    if (!categoryEl.value) categoryEl.value='all';
  }

  // Initialize Year dropdown with all years
  setYearOptionsAll();

  renderTagBar('all');
  applyFilters();

  // Keep selected state synced when checkboxes are toggled
  document.addEventListener('change', (e) => {
    const t = e.target;
    if (!(t instanceof Element)) return;
    if (!t.matches('.selection-checkbox')) return;
    syncSelectedPapersFromDom();
    if (ST.onlyShowSelected) applyFilters();
  });

  const yearEl = document.getElementById('yearFilter');
  if (yearEl) yearEl.addEventListener('change', applyFilters);

  const searchEl = document.getElementById('searchInput');
  if (searchEl){
    let t;
    searchEl.addEventListener('input', ()=>{
      clearTimeout(t);
      t = setTimeout(applyFilters, 140);
    });
  }

  const clearBtn = document.querySelector('[data-action="clear-all"]');
  if (clearBtn){
    clearBtn.addEventListener('click', e=>{
      e.preventDefault();
      resetAllFilters();
    });
  }

  // Reorder in‑card tags once cards are in DOM
  reorderAllPaperTags();
});

// Remember last category to avoid unnecessary work
let __lastCategory = 'all';

// Build Year dropdown for a given category scope (uses the index you already build)
function setYearOptionsForCategory(catKey){
  const yearEl = document.getElementById('yearFilter');
  const idx = window.__FILTER_INDEX;
  if (!yearEl || !idx || !idx.categoryYears) return;

  const key = (!catKey || catKey === 'all') ? 'all' : normalizeCategory(catKey);
  const years = idx.categoryYears[key] || idx.categoryYears.all || [];

  // Rebuild options: All Years + sorted years
  yearEl.innerHTML = '';
  const optAll = document.createElement('option');
  optAll.value = 'all'; optAll.textContent = 'All Years';
  yearEl.appendChild(optAll);

  Array.from(new Set(years))
    .sort((a,b)=>parseInt(b)-parseInt(a))
    .forEach(y=>{
      const o = document.createElement('option');
      o.value = y; o.textContent = y;
      yearEl.appendChild(o);
    });

  // Always reset to All when category changes
  yearEl.value = 'all';
}

// Category change: reset Year -> repopulate -> render tags -> filter
function onCategoryChange(){
  const categoryEl = document.getElementById('categoryFilter');
  if (!categoryEl) return;
  const newKey = normalizeCategory(categoryEl.value || 'all');

  if (newKey !== __lastCategory){
    setYearOptionsForCategory(newKey);
    __lastCategory = newKey;
  }

  renderTagBar(newKey);
  applyFilters(); // will rebuild chips and numbering
}

// Wire up safely (does not remove your existing init)
document.addEventListener('DOMContentLoaded', ()=>{
  const categoryEl = document.getElementById('categoryFilter');
  if (categoryEl){
    categoryEl.removeEventListener?.('change', onCategoryChange);
    categoryEl.addEventListener('change', onCategoryChange);
  }
});

/* ---------- In-Card Tag Reordering & Styling ----------*/
function reorderAllPaperTags(){
  const masterIndex = (typeof MASTER_TAG_ORDER !== 'undefined')
        ? MASTER_TAG_ORDER.reduce((m,t,i)=>{m[ norm(t) ]=i;return m;}, {})
        : {};
  const highlighted = window.HIGHLIGHTED_TAGS || new Set();

  function norm(s){
    return (s||'')
      .toLowerCase()
      .replace(/&/g,'and')
      .replace(/\s+/g,' ')
      .trim();
  }

  document.querySelectorAll('.paper-row').forEach(row=>{
    const container = row.querySelector('.paper-tags');
    if(!container) return;

    const primaryRaw = row.getAttribute('data-primary-category') || '';
    const primaryN = norm(primaryRaw);
    if(!primaryN) return;

    const tags = Array.from(container.querySelectorAll('.paper-tag'));
    if(!tags.length){
      // If no tags but we have a primary category, inject it.
      const injected = document.createElement('span');
      injected.className = 'paper-tag tag-primary injected-primary';
      injected.textContent = primaryRaw;
      container.appendChild(injected);
      return;
    }

    let primaryEl = null;
    const highlightedEls = [];
    const otherEls = [];

    tags.forEach(el=>{
      const rawText = el.textContent.trim();
      const nTxt = norm(rawText);

      // Clear any previous classification (allow idempotent re-run)
      el.classList.remove('tag-primary','tag-highlighted-group');

      if(!primaryEl && nTxt === primaryN){
        primaryEl = el;
      } else if (highlighted.has(rawText) || highlighted.has(rawText.replace(/&/g,'and'))){
        highlightedEls.push(el);
      } else {
        otherEls.push(el);
      }
    });

    // If primary tag not present among existing tags -> inject it.
    if(!primaryEl){
      const injected = document.createElement('span');
      injected.className = 'paper-tag tag-primary injected-primary';
      injected.textContent = primaryRaw;
      primaryEl = injected;
    } else {
      primaryEl.classList.add('tag-primary');
      // Ensure it is not also treated as highlighted group
      highlightedEls.forEach((el,i)=>{
        if (el === primaryEl){
          highlightedEls.splice(i,1);
        }
      });
    }

    // Remove any accidental tag-highlighted-group from the primary
    primaryEl.classList.remove('tag-highlighted-group');

    // Sort helper
    function sortByMaster(a,b){
      const ta = norm(a.textContent);
      const tb = norm(b.textContent);
      const ia = (ta in masterIndex) ? masterIndex[ta] : 999999;
      const ib = (tb in masterIndex) ? masterIndex[tb] : 999999;
      if (ia !== ib) return ia - ib;
      return a.textContent.localeCompare(b.textContent);
    }
    highlightedEls.sort(sortByMaster);
    otherEls.sort(sortByMaster);

    // Mark highlighted group headers
    highlightedEls.forEach(el=>el.classList.add('tag-highlighted-group'));

    // Rebuild order
    const newOrder = [primaryEl, ...highlightedEls, ...otherEls];

    // If primary was injected, prepend; else re-append in order
    if (primaryEl.classList.contains('injected-primary') && !primaryEl.isConnected){
      container.prepend(primaryEl);
    }

    newOrder.forEach(el=>{
      if(!el.isConnected) container.appendChild(el);
      else container.appendChild(el); // move to end in new order
    });
  });
}

// Call again after initial load (in case existing call happened before cards ready)
document.addEventListener('DOMContentLoaded', ()=>{
  reorderAllPaperTags();
});

// Expose for debug
window.__reorderAllPaperTags = reorderAllPaperTags;

})(); // end IIFE

