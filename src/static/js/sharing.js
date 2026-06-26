function fallbackCopyText(text) {
    const textArea = document.createElement("textarea");
    textArea.value = text;
    textArea.style.position = "fixed";
    textArea.style.top = "0";
    textArea.style.left = "0";
    textArea.style.width = "2em";
    textArea.style.height = "2em";
    textArea.style.padding = "0";
    textArea.style.border = "none";
    textArea.style.outline = "none";
    textArea.style.boxShadow = "none";
    textArea.style.background = "transparent";
    document.body.appendChild(textArea);
    textArea.focus();
    textArea.select();
    try {
        const successful = document.execCommand('copy');
        document.body.removeChild(textArea);
        return successful;
    } catch (err) {
        document.body.removeChild(textArea);
        return false;
    }
}

async function copyTextToClipboard(text) {
    if (navigator.clipboard) {
        try {
            await navigator.clipboard.writeText(text);
            return true;
        } catch (e) {
            // fall through
        }
    }
    return fallbackCopyText(text);
}

function showShareModal() {
    if (state.selectedPapers.size === 0) {
        alert('Please select at least one paper to share.');
        return;
    }
    const shareUrl = new URL(window.location.href);
    shareUrl.searchParams.set('selected', Array.from(state.selectedPapers).join(','));
    shareUrl.searchParams.set('show_selected', 'true');
    shareUrl.hash = ''; // Clear hash for selection links
    document.getElementById('shareUrl').value = shareUrl.toString();
    document.getElementById('shareModal').classList.add('show');
}

async function copyPaperLink(event, paperId) {
    event.stopPropagation();
    const btn = event.currentTarget;
    const url = new URL(window.location.href);
    url.searchParams.set('selected', paperId);
    url.searchParams.set('show_selected', 'true');
    url.hash = ''; // Clear hash for selection links
    
    const success = await copyTextToClipboard(url.toString());
    if (success) {
        const origText = btn.innerHTML;
        btn.innerHTML = '🔗 Copied!';
        btn.classList.add('copied');
        setTimeout(() => {
            btn.innerHTML = origText;
            btn.classList.remove('copied');
        }, 1500);
    } else {
        alert('Failed to copy link. Please copy manually.');
    }
}

function hideShareModal() {
    document.getElementById('shareModal').classList.remove('show');
}

async function copyShareLink() {
    const shareUrl = document.getElementById('shareUrl');
    const success = await copyTextToClipboard(shareUrl.value);
    if (success) {
        const copyButton = document.querySelector('.share-url-container .control-button');
        const origText = copyButton.innerHTML;
        copyButton.innerHTML = '<i class="fas fa-check"></i> Copied!';
        setTimeout(() => {
            copyButton.innerHTML = origText;
        }, 2000);
    } else {
        alert('Failed to copy link. Please copy manually.');
    }
}

async function copyBitcoinAddress() {
    const address = document.querySelector('.bitcoin-address').textContent;
    const success = await copyTextToClipboard(address);
    if (success) {
        const button = document.querySelector('.copy-button');
        const originalText = button.innerHTML;
        button.innerHTML = '<i class="fas fa-check"></i> Copied!';
        setTimeout(() => {
            button.innerHTML = originalText;
        }, 2000);
    }
}

function applyURLParams() {
    const params = new URLSearchParams(window.location.search);
    
    // First, check if we have selected papers
    const selPapers = params.get('selected');
    if (selPapers) {
        const arr = selPapers.split(',');
        if (arr.length > 0) {
            // Enter selection mode
            if (!state.isSelectionMode) {
                toggleSelectionMode();
            }
            
            // Select the papers first
            arr.forEach(id => {
                const row = document.querySelector(`.paper-row[data-id="${id}"]`);
                if (row) {
                    const cb = row.querySelector('.selection-checkbox');
                    if (cb) {
                        cb.checked = true;
                        togglePaperSelection(id, cb);
                    }
                }
            });
            
            // Then check if we should show only selected papers
            const showSelected = params.get('show_selected');
            if (showSelected === 'true') {
                if (typeof toggleSelectedOnly === 'function') {
                    toggleSelectedOnly(true);
                } else {
                    state.onlyShowSelected = true;
                    filterPapers();
                }

                // Auto-scroll to the papers grid
                const grid = document.querySelector('.papers-grid');
                if (grid) {
                    setTimeout(() => {
                        grid.scrollIntoView({ behavior: 'smooth', block: 'start' });
                    }, 500);
                }
            }
        }
    }
    
    // Handle other filters
    const searchTerm = params.get('search');
    if (searchTerm) {
        searchInput.value = searchTerm;
    }
    
    const yr = params.get('year');
    if (yr) {
        yearFilter.value = yr;
    }

    const inc = params.get('include');
    if (inc) {
        state.includeTags = new Set(inc.split(','));
        state.includeTags.forEach(t => {
            const tf = document.querySelector(`.tag-filter[data-tag="${t}"]`);
            if (tf) tf.classList.add('include');
        });
    }
    
    const exc = params.get('exclude');
    if (exc) {
        state.excludeTags = new Set(exc.split(','));
        state.excludeTags.forEach(t => {
            const tf = document.querySelector(`.tag-filter[data-tag="${t}"]`);
            if (tf) tf.classList.add('exclude');
        });
    }
    
    // Final filter application
    filterPapers();
}

window.copyPaperLink = copyPaperLink;