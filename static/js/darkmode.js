window.addEventListener('DOMContentLoaded', (event) => {
    // Check for the saved theme in localStorage and apply it to the body
    const savedTheme = localStorage.getItem('theme');
    if (savedTheme) {
        document.body.className = savedTheme;
    }

    // Handle the button click to switch between themes
    document.querySelector('#toggleButton').addEventListener('click', () => {
        // Switch the current class of the body
        if (document.body.classList.contains('dark')) {
            document.body.classList.remove('dark');
            localStorage.setItem('theme', '');
        } else {
            document.body.classList.add('dark');
            localStorage.setItem('theme', 'dark');
        }
    });
});
