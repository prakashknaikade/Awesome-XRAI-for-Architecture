// Navigation controls
function scrollToTop() {
    window.scrollTo({
        top: 0,
        behavior: 'smooth'
    });
}

function scrollToBottom() {
    window.scrollTo({
        top: document.documentElement.scrollHeight,
        behavior: 'smooth'
    });
}

// Update scroll progress
function updateScrollProgress() {
    const winScroll = document.documentElement.scrollTop;
    const height = document.documentElement.scrollHeight - document.documentElement.clientHeight;
    const scrolled = Math.round((winScroll / height) * 100);
    document.querySelector('.scroll-progress').textContent = `${scrolled}%`;
}

// Filter status functionality
function updateFilterStatus() {
    const visiblePapers = document.querySelectorAll('.paper-row.visible').length;
    const totalPapers = document.querySelectorAll('.paper-row').length;
    
    document.getElementById('visibleCount').textContent = visiblePapers;
    document.getElementById('totalCount').textContent = totalPapers;

    const activeFiltersEl = document.getElementById('activeFilters');
    activeFiltersEl.innerHTML = '';

    // Search filter
    const searchTerm = document.getElementById('searchInput').value;
    if (searchTerm) {
        const searchTag = createFilterTag('search', 'Search Filter', searchTerm);
        searchTag.querySelector('button').addEventListener('click', () => {
            document.getElementById('searchInput').value = '';
            filterPapers();
        });
        activeFiltersEl.appendChild(searchTag);
    }

    // Year filter
    const yearFilter = document.getElementById('yearFilter').value;
    if (yearFilter !== 'all') {
        const yearTag = createFilterTag('year', 'Year Filter', yearFilter);
        yearTag.querySelector('button').addEventListener('click', () => {
            document.getElementById('yearFilter').value = 'all';
            filterPapers();
        });
        activeFiltersEl.appendChild(yearTag);
    }

    // Tag filters
    document.querySelectorAll('.tag-filter').forEach(tagEl => {
        if (tagEl.classList.contains('include') || tagEl.classList.contains('exclude')) {
            const tagText = tagEl.getAttribute('data-tag');
            const type = tagEl.classList.contains('include') ? 'Including' : 'Excluding';
            const tagTag = createFilterTag('tag', `${type} Tag`, tagText);
            
            // Update the click handler to completely remove the tag
            tagTag.querySelector('button').addEventListener('click', () => {
                tagEl.classList.remove('include', 'exclude');
                state.includeTags.delete(tagText);
                state.excludeTags.delete(tagText);
                filterPapers();
            });
            
            activeFiltersEl.appendChild(tagTag);
        }
    });
}

function createFilterTag(type, title, info) {
    const tag = document.createElement('div');
    tag.className = `filter-tag ${type}`;
    
    tag.innerHTML = `
        <div class="filter-tag-content">
            <div class="filter-tag-title">${title}</div>
            <div class="filter-tag-info">${info}</div>
        </div>
        <button class="preview-remove" onclick="event.stopPropagation();" aria-label="Remove filter">
            <i class="fas fa-times"></i>
        </button>
    `;
    
    return tag;
}

function clearAllFilters() {
    // Clear search
    document.getElementById('searchInput').value = '';
    
    // Reset year filter
    document.getElementById('yearFilter').value = 'all';
    
    // Clear all tag filters completely (don't toggle through states)
    document.querySelectorAll('.tag-filter').forEach(tag => {
        tag.classList.remove('include', 'exclude');
        state.includeTags.delete(tag.getAttribute('data-tag'));
        state.excludeTags.delete(tag.getAttribute('data-tag'));
    });
    
    // Update the UI
    filterPapers();
    updateFilterStatus();
}


// Initialize
document.addEventListener('DOMContentLoaded', function() {
    // Set initial paper counts
    updateFilterStatus();
    
    // Add scroll listener
    window.addEventListener('scroll', updateScrollProgress);
    
    // Override the existing filterPapers function to update filter status
    const originalFilterPapers = window.filterPapers;
    window.filterPapers = function() {
        if (typeof originalFilterPapers === 'function') {
            originalFilterPapers();
        }
        updateFilterStatus();
    };

    // Handle direct paper link anchoring with smooth scroll and highlight pulse
    window.addEventListener('hashchange', handleHashNavigation);
    
    // Check hash on initial load
    setTimeout(handleHashNavigation, 250);
});

function handleHashNavigation() {
    const hash = window.location.hash;
    if (hash && hash.startsWith('#')) {
        const id = hash.substring(1);
        const row = document.querySelector(`.paper-row[data-id="${id}"]`);
        if (row) {
            // First reset all filters to ensure it's visible
            if (typeof resetAllFilters === 'function') {
                resetAllFilters();
            }
            
            // Scroll to the card and flash it
            setTimeout(() => {
                row.scrollIntoView({ behavior: 'smooth', block: 'center' });
                const card = row.querySelector('.paper-card');
                if (card) {
                    card.classList.add('highlight-pulse');
                    setTimeout(() => {
                        card.classList.remove('highlight-pulse');
                    }, 2500);
                }
            }, 100);
        }
    }
}
window.handleHashNavigation = handleHashNavigation;