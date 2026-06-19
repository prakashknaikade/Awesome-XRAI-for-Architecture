/**
 * Theme management functionality
 */

// Theme state
let currentTheme = 'auto'; // default theme

// Initialize theme system
function initializeTheme() {
    // Get saved theme from localStorage or default to 'auto'
    const savedTheme = localStorage.getItem('theme') || 'auto';
    setTheme(savedTheme);
}

// Set theme
function setTheme(theme) {
    currentTheme = theme;
    document.documentElement.setAttribute('data-theme', theme);
    localStorage.setItem('theme', theme);
    
    // Update the theme toggle button tooltip
    updateThemeTooltip();
}

// Toggle between themes: light -> dark -> auto -> light
function toggleTheme() {
    // Add transitioning class to document root to enable smooth transition
    document.documentElement.classList.add('theme-transitioning');
    
    const themes = ['light', 'dark', 'auto'];
    const currentIndex = themes.indexOf(currentTheme);
    const nextIndex = (currentIndex + 1) % themes.length;
    const nextTheme = themes[nextIndex];
    
    setTheme(nextTheme);
    
    // Remove transition class after the transition finishes (130ms)
    setTimeout(() => {
        document.documentElement.classList.remove('theme-transitioning');
    }, 130);
}

// Update theme button tooltip
function updateThemeTooltip() {
    const themeButton = document.querySelector('.theme-toggle-btn .tooltip');
    if (themeButton) {
        const themeNames = {
            'light': 'Light Theme',
            'dark': 'Dark Theme', 
            'auto': 'Auto Theme'
        };
        themeButton.textContent = themeNames[currentTheme] || 'Toggle Theme';
    }
}

// Listen for system theme changes when in auto mode
function handleSystemThemeChange() {
    if (currentTheme === 'auto') {
        // Force a repaint to apply the new auto theme
        document.documentElement.style.display = 'none';
        document.documentElement.offsetHeight; // Trigger reflow
        document.documentElement.style.display = '';
    }
}

// Set up system theme change listener
if (window.matchMedia) {
    window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', handleSystemThemeChange);
}

// Export functions for global access
window.toggleTheme = toggleTheme;
window.setTheme = setTheme;
window.initializeTheme = initializeTheme;