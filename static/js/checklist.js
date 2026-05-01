document.addEventListener('DOMContentLoaded', async () => {
    const checkboxes = document.querySelectorAll('.checklist-checkbox');
    const progressBar = document.getElementById('progress-fill');
    const countText = document.getElementById('progress-count');
    const resetBtn = document.getElementById('reset-progress-btn');
    const statusRadios = document.querySelectorAll('input[name="status"]');

    const countryMeta = document.querySelector('meta[name="country_code"]');
    const roleMeta = document.querySelector('meta[name="user_role"]');
    const cCode = countryMeta ? countryMeta.content : 'IN';
    const role = roleMeta ? roleMeta.content : 'Voter';

    // ── Load saved state from Firebase (or session fallback) ─────────────────
    async function loadState() {
        try {
            const resp = await fetch(`/api/checklist-state?country=${cCode}&role=${role}`);
            if (!resp.ok) return;
            const state = await resp.json();
            checkboxes.forEach(cb => {
                if (state[cb.id] === true) {
                    cb.checked = true;
                    cb.closest('.checklist-item')?.classList.add('completed');
                }
            });
        } catch (e) {
            console.warn('Could not load checklist state:', e);
        }
        updateProgressUI();
    }

    // ── Save state to Firebase (or session fallback) ──────────────────────────
    async function saveState() {
        const state = {};
        checkboxes.forEach(cb => { state[cb.id] = cb.checked; });
        try {
            await fetch(`/api/checklist-state?country=${cCode}&role=${role}`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(state)
            });
        } catch (e) {
            console.warn('Could not save checklist state:', e);
        }
    }

    // ── Progress UI ───────────────────────────────────────────────────────────
    function updateProgressUI() {
        if (checkboxes.length === 0) return;
        let checked = 0;
        checkboxes.forEach(cb => { if (cb.checked) checked++; });
        const pct = Math.round((checked / checkboxes.length) * 100);
        if (progressBar) progressBar.style.width = pct + '%';
        if (countText) countText.textContent = `${checked} / ${checkboxes.length} done`;

        // Update SVG ring
        const ring = document.querySelector('circle[stroke="var(--color-primary)"]');
        if (ring) {
            const circumference = 163;
            const offset = circumference - (pct / 100) * circumference;
            ring.setAttribute('stroke-dashoffset', offset);
        }
    }

    // ── Checkbox change handler ───────────────────────────────────────────────
    checkboxes.forEach(cb => {
        cb.addEventListener('change', async (e) => {
            const item = e.target.closest('.checklist-item');
            item?.classList.toggle('completed', e.target.checked);
            updateProgressUI();
            await saveState();
        });
    });

    // ── Reset button ─────────────────────────────────────────────────────────
    if (resetBtn) {
        resetBtn.addEventListener('click', async () => {
            if (!confirm('Reset all progress for this checklist?')) return;
            checkboxes.forEach(cb => {
                cb.checked = false;
                cb.closest('.checklist-item')?.classList.remove('completed');
            });
            updateProgressUI();
            await saveState();
        });
    }

    // ── Status radio — reload page with new status param ─────────────────────
    statusRadios.forEach(radio => {
        radio.addEventListener('change', () => {
            const url = new URL(window.location.href);
            url.searchParams.set('status', radio.value);
            window.location.href = url.toString();
        });
    });

    // ── Role changed (from top-bar pills) — reload to refresh checklist ───────
    window.addEventListener('roleChanged', () => {
        window.location.reload();
    });

    // ── Init ──────────────────────────────────────────────────────────────────
    await loadState();
});