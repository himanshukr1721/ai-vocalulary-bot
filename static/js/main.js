// Function to display a confirmation alert when navigating back to the dashboard
document.addEventListener('DOMContentLoaded', () => {
    const backButton = document.querySelector('a[href*="dashboard"]');
    
    if (backButton) {
        backButton.addEventListener('click', (event) => {
            const confirmNavigation = confirm("Are you sure you want to go back to the dashboard?");
            if (!confirmNavigation) {
                event.preventDefault();
            }
        });
    }
});

// Function to highlight synonyms and antonyms on hover
document.addEventListener('DOMContentLoaded', () => {
    const synonymItems = document.querySelectorAll('ul.list-disc li');
    
    synonymItems.forEach(item => {
        item.addEventListener('mouseover', () => {
            item.style.backgroundColor = '#e2e8f0'; // Light gray background
        });
        item.addEventListener('mouseout', () => {
            item.style.backgroundColor = 'transparent';
        });
    });
});