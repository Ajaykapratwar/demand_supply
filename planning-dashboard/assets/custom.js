document.addEventListener('click', function(e) {
    var target = e.target.closest('#theme-toggle-btn');
    if (target) {
        var html = document.documentElement;
        var current_theme = html.getAttribute('data-theme') || 'dark';
        var new_theme = (current_theme === 'dark') ? 'light' : 'dark';
        html.setAttribute('data-theme', new_theme);
        
        var icon = document.getElementById('theme-icon');
        if (icon) {
            icon.className = (new_theme === 'dark') ? 'bi bi-moon-stars' : 'bi bi-sun';
        }
    }
});
