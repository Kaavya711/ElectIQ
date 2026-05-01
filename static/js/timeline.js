document.addEventListener('DOMContentLoaded', () => {
    const timelineItems = document.querySelectorAll('.timeline-item');
    const toggleButtons = document.querySelectorAll('.toggle-details-btn');

    // Toggle details expansion
    toggleButtons.forEach(btn => {
        btn.addEventListener('click', (e) => {
            const item = e.target.closest('.timeline-item');
            const details = item.querySelector('.timeline-details');
            
            if (details.classList.contains('open')) {
                details.classList.remove('open');
                e.target.textContent = '↓ What this means for you';
                item.classList.remove('active');
            } else {
                details.classList.add('open');
                e.target.textContent = '↑ Hide details';
                item.classList.add('active');
            }
        });
    });

    // Update details text when role changes without page reload
    window.addEventListener('roleChanged', (e) => {
        const newRole = e.detail.role;
        const noteContainers = document.querySelectorAll('.role-note-container');
        
        noteContainers.forEach(container => {
            const voterText = container.dataset.voter;
            const candidateText = container.dataset.candidate;
            const learnerText = container.dataset.learner;
            
            const label = container.querySelector('.role-note-label');
            const content = container.querySelector('.role-note-content');
            
            if (newRole === 'Voter') {
                label.textContent = 'FOR VOTERS';
                content.textContent = voterText;
            } else if (newRole === 'Candidate') {
                label.textContent = 'FOR CANDIDATES';
                content.textContent = candidateText;
            } else {
                label.textContent = 'CIVIC CONTEXT';
                content.textContent = learnerText;
            }
        });
    });

    // Scroll Animation using Intersection Observer
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = 1;
                entry.target.style.transform = 'translateX(0)';
                observer.unobserve(entry.target);
            }
        });
    }, { threshold: 0.2 });

    timelineItems.forEach((item, index) => {
        item.style.opacity = 0;
        item.style.transition = 'all 0.5s ease ' + (index * 0.1) + 's';
        
        if (index % 2 === 0) {
            item.style.transform = 'translateX(-40px)';
        } else {
            item.style.transform = 'translateX(40px)';
        }
        
        observer.observe(item);
    });
});
