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
    const themes = ['light', 'dark', 'auto'];
    const currentIndex = themes.indexOf(currentTheme);
    const nextIndex = (currentIndex + 1) % themes.length;
    const nextTheme = themes[nextIndex];
    
    setTheme(nextTheme);
    
    // Show a brief notification
    showThemeNotification(nextTheme);
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

// Show theme change notification
function showThemeNotification(theme) {
    // Remove existing notification
    const existingNotification = document.querySelector('.theme-notification');
    if (existingNotification) {
        existingNotification.remove();
    }
    
    // Create notification
    const notification = document.createElement('div');
    notification.className = 'theme-notification';
    notification.innerHTML = `
        <i class="fas fa-${theme === 'light' ? 'sun' : theme === 'dark' ? 'moon' : 'circle-half-stroke'}"></i>
        ${theme.charAt(0).toUpperCase() + theme.slice(1)} theme activated
    `;
    
    // Style the notification
    notification.style.cssText = `
        position: fixed;
        top: 80px;
        left: 20px;
        background: var(--bg-secondary);
        color: var(--text-primary);
        padding: 12px 16px;
        border-radius: 8px;
        box-shadow: 0 4px 12px var(--shadow-color);
        z-index: 1001;
        font-size: 14px;
        font-weight: 500;
        display: flex;
        align-items: center;
        gap: 8px;
        opacity: 0;
        transform: translateX(-20px);
        transition: all 0.3s ease;
        pointer-events: none;
    `;
    
    document.body.appendChild(notification);
    
    // Animate in
    setTimeout(() => {
        notification.style.opacity = '1';
        notification.style.transform = 'translateX(0)';
    }, 10);
    
    // Remove after delay
    setTimeout(() => {
        notification.style.opacity = '0';
        notification.style.transform = 'translateX(-20px)';
        setTimeout(() => {
            if (notification.parentNode) {
                notification.remove();
            }
        }, 300);
    }, 2000);
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