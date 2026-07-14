// ElectroStock Main JavaScript Setup
document.addEventListener('DOMContentLoaded', () => {
    console.log('⚡ ElectroStock Core Assets Loaded successfully.');
    
    // Initialize Lucide Icons
    if (typeof lucide !== 'undefined') {
        lucide.createIcons();
    }
    
    // Theme Switcher Logic
    const themeToggleBtn = document.getElementById('themeToggle');
    const themeIconActive = document.getElementById('theme-icon-active');
    const themeItems = document.querySelectorAll('[data-theme-value]');
    
    if (themeToggleBtn && themeIconActive) {
        // Icon mapping for premium Lucide theme icons
        const iconMap = {
            light: 'sun-medium',
            dark: 'moon-star',
            system: 'monitor-smartphone'
        };

        const getSystemTheme = () => {
            return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
        };

        const applyTheme = (theme, animate = false) => {
            const resolvedTheme = theme === 'system' ? getSystemTheme() : theme;
            
            // Apply theme data attribute on html tag
            document.documentElement.setAttribute('data-theme', resolvedTheme);
            window.dispatchEvent(new CustomEvent('theme-changed', { detail: resolvedTheme }));
            
            // Store theme in local storage
            localStorage.setItem('theme', theme);
            
            // Update active states on switcher dropdown list items
            themeItems.forEach(item => {
                const itemTheme = item.getAttribute('data-theme-value');
                if (itemTheme === theme) {
                    item.classList.add('active');
                } else {
                    item.classList.remove('active');
                }
            });

            // Update main toggle button icon with rotate and fade transition
            const targetIconName = iconMap[theme] || 'sun-medium';
            
            if (animate) {
                themeIconActive.style.transform = 'rotate(180deg) scale(0.5)';
                themeIconActive.style.opacity = '0';
                
                setTimeout(() => {
                    themeIconActive.setAttribute('data-lucide', targetIconName);
                    if (typeof lucide !== 'undefined') {
                        lucide.createIcons();
                    }
                    themeIconActive.style.transform = 'rotate(360deg) scale(1)';
                    themeIconActive.style.opacity = '1';
                    
                    // Reset inline transform after transition is completed
                    setTimeout(() => {
                        themeIconActive.style.transform = '';
                    }, 250);
                }, 150);
            } else {
                themeIconActive.setAttribute('data-lucide', targetIconName);
                if (typeof lucide !== 'undefined') {
                    lucide.createIcons();
                }
            }
        };

        // Listen for user clicks to switch themes
        themeItems.forEach(item => {
            item.addEventListener('click', () => {
                const themeVal = item.getAttribute('data-theme-value');
                applyTheme(themeVal, true);
            });
        });

        // Listen for OS system theme changes
        window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', () => {
            const currentSavedTheme = localStorage.getItem('theme') || 'system';
            if (currentSavedTheme === 'system') {
                applyTheme('system', true);
            }
        });

        // Initialize active theme on page load
        const initialTheme = localStorage.getItem('theme') || 'system';
        applyTheme(initialTheme, false);
    }
});
