// Single global state (attach to window so other scripts share it)
window.state = window.state || {
  includeTags: new Set(),
  excludeTags: new Set(),
  selectedPapers: new Set(),
  onlyShowSelected: false
};

// Highlighted tags (shared)
window.HIGHLIGHTED_TAGS = window.HIGHLIGHTED_TAGS || new Set([
  "Generative Design and Form Finding",
  "Parametric, Computational and Algorithmic Design",
  "Design Space Exploration",
  "Performance-Driven Design",
  "3D Reconstruction",
  "Predictive Analytics and Performance Optimization",
  "Floor Plan Reconstruction and Parametrization",
  "Quality Control and Validation",
  "Digital Documentation and Archiving",
  "Predictive Conservation and Risk Assessment",
  "Virtual Reality Experiences and Education",
  "AI for Energy Performance Optimization",
  "Sustainable Buildings",
  "Smart Building Systems and IoT Integration",
  "AI-Powered Real Estate Valuation",
  "Portfolio Management and Investment Analysis",
  "Virtual Property Tours and Marketing",
  "XRAI for AEC",
  "Occupant Behavior Analysis and Spatial Optimization",
  "Cross-Modal Intelligence and Multimodal Integration",
  "Review Paper", 
  "Dataset", 
  "Case Study", 
  "Tool/Library",

]);

function isHighlightedTag(tag){
  if (window.HIGHLIGHTED_TAGS.has(tag)) return true;
  const norm = tag.replace("&","and");
  for (const h of window.HIGHLIGHTED_TAGS) {
    if (h.replace("&","and") === norm) return true;
  }
  return false;
}

function clearAllFilters(){
  if (typeof window.resetAllFilters === 'function'){
    window.resetAllFilters();
  } else {
    // Fallback (very early load)
    window.state.includeTags.clear();
    window.state.excludeTags.clear();
    const searchEl = document.getElementById('searchInput');
    const yearEl = document.getElementById('yearFilter');
    const categoryEl = document.getElementById('categoryFilter');
    if (searchEl) searchEl.value = '';
    if (yearEl) yearEl.value = 'all';
    if (categoryEl) categoryEl.value = 'all';
    document.querySelectorAll('.paper-row').forEach(r=>r.classList.add('visible'));
    const tagWrap = document.getElementById('tagFilters');
    if (tagWrap) tagWrap.querySelectorAll('.tag-filter').forEach(p=>p.classList.remove('include','exclude'));
  }
}
window.clearAllFilters = clearAllFilters;