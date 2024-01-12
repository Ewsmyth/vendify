let currentSlide = 0;
let touchStartX = 0;

function showSlide(index) {
    const slides = document.querySelectorAll('.slide');
    slides.forEach((slide, i) => {
        slide.style.display = i === index ? 'block' : 'none';
    });
}

function nextSlide() {
    currentSlide = (currentSlide + 1) % document.querySelectorAll('.slide').length;
    showSlide(currentSlide);
}

function prevSlide() {
    currentSlide = (currentSlide - 1 + document.querySelectorAll('.slide').length) % document.querySelectorAll('.slide').length;
    showSlide(currentSlide);
}

function handleTouchStart(event) {
    touchStartX = event.touches[0].clientX;
}

function handleTouchEnd(event) {
    const touchEndX = event.changedTouches[0].clientX;
    const swipeThreshold = 50; // Adjust this value as needed

    if (touchEndX < touchStartX - swipeThreshold) {
        nextSlide();
    } else if (touchEndX > touchStartX + swipeThreshold) {
        prevSlide();
    }
}

// Initial slide display
document.addEventListener('DOMContentLoaded', () => {
    showSlide(currentSlide);

    // Add touch event listeners
    const slider = document.querySelector('.slider'); // Replace with your actual slider element
    slider.addEventListener('touchstart', handleTouchStart);
    slider.addEventListener('touchend', handleTouchEnd);
});


// Expand button code
document.addEventListener('DOMContentLoaded', function() {
    const expandableText = document.getElementById('expandableText');
    const toggleButton = document.getElementById('toggleButton');

    toggleButton.addEventListener('click', function() {
        expandableText.classList.toggle('expanded');
        toggleButton.textContent = expandableText.classList.contains('expanded') ? 'Show less' : 'Show more';
    });
});