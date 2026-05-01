document.addEventListener('DOMContentLoaded', () => {
    // Role selection handling
    const roleSelectors = document.querySelectorAll('.role-pill');
    if (roleSelectors.length > 0) {
        roleSelectors.forEach(pill => {
            pill.addEventListener('click', async (e) => {
                const role = e.target.dataset.role;

                roleSelectors.forEach(p => {
                    p.classList.remove('active');
                    p.setAttribute('aria-pressed', 'false');
                });
                e.target.classList.add('active');
                e.target.setAttribute('aria-pressed', 'true');

                try {
                    await fetch('/set-role', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ role })
                    });
                    window.dispatchEvent(new CustomEvent('roleChanged', { detail: { role } }));
                } catch (error) {
                    console.error("Failed to update role", error);
                }
            });
        });

        // Set initial aria-pressed
        roleSelectors.forEach(pill => {
            pill.setAttribute('role', 'button');
            pill.setAttribute('aria-pressed', pill.classList.contains('active') ? 'true' : 'false');
        });
    }

    // Mobile sidebar toggle with aria-expanded
    const menuToggle = document.getElementById('menu-toggle');
    const sidebar = document.getElementById('sidebar');
    if (menuToggle && sidebar) {
        menuToggle.addEventListener('click', () => {
            const isOpen = sidebar.classList.toggle('open');
            menuToggle.setAttribute('aria-expanded', String(isOpen));
        });

        // Close sidebar on outside click (mobile UX)
        document.addEventListener('click', (e) => {
            if (sidebar.classList.contains('open') &&
                !sidebar.contains(e.target) &&
                e.target !== menuToggle) {
                sidebar.classList.remove('open');
                menuToggle.setAttribute('aria-expanded', 'false');
            }
        });
    }
});