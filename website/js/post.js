document.addEventListener("DOMContentLoaded", function() {
    const displayedImage = document.getElementById('displayedImage');
    const fileUploadDivs = document.querySelectorAll('.file-upload-div');
    const displayMedia = document.getElementById('displayMedia');
    const mediaUploadDiv = document.getElementById('mediaUploadDiv');
    const mediaInput = document.getElementById('media_files');

    displayedImage.style.display = 'none';
    displayMedia.style.display = 'none';

    fileUploadDivs.forEach(fileUploadDiv => {
        const fileInput = fileUploadDiv.nextElementSibling;

        fileUploadDiv.addEventListener('click', function() {
            fileInput.click();
        });

        fileInput.addEventListener('change', function(event) {
            const file = event.target.files[0];
            if (file) {
                const reader = new FileReader();
                reader.onload = function(e) {
                    displayedImage.src = e.target.result;
                    displayedImage.style.display = 'block';
                }
                reader.readAsDataURL(file);
            }
        });
    });

    mediaUploadDiv.addEventListener('click', function() {
        mediaInput.click();
    });

    mediaInput.addEventListener('change', function(event) {
        const files = event.target.files;
        if (files.length > 0) {
            displayMedia.innerHTML = '';
            for (let i = 0; i < files.length; i++) {
                const file = files[i];
                const reader = new FileReader();
                reader.onload = function(e) {
                    const mediaElement = document.createElement(file.type.startsWith('image') ? 'img' : 'video');
                    mediaElement.src = e.target.result;
                    mediaElement.alt = 'Uploaded Media';
                    mediaElement.classList.add('media-element');
                    displayMedia.appendChild(mediaElement);
                }
                reader.readAsDataURL(file);
            }
            displayMedia.style.display = 'flex';
        }
    });

    const postMediaDivs = document.querySelectorAll('.post-media-div');
    postMediaDivs.forEach(postElement => {
        const postId = postElement.dataset.postId;
        fetch(`/get_media_count/${postId}`)
            .then(response => response.json())
            .then(data => {
                const mediaCount = data.media_count;

                const prevButton = postElement.querySelector('.prev-button');
                const nextButton = postElement.querySelector('.next-button');
                const slider = postElement.querySelector('.media-slider');
                const slides = slider.children;
                let currentIndex = 0; // Add this line to declare currentIndex

                Array.from(slides).forEach((slide, index) => {
                    if (index !== currentIndex) {
                        slide.style.display = 'none';
                    }
                });

                prevButton.addEventListener('click', () => {
                    slides[currentIndex].style.display = 'none';
                    currentIndex = (currentIndex - 1 + mediaCount) % mediaCount;
                    slides[currentIndex].style.display = 'block';
                });

                nextButton.addEventListener('click', () => {
                    slides[currentIndex].style.display = 'none';
                    currentIndex = (currentIndex + 1) % mediaCount;
                    slides[currentIndex].style.display = 'block';
                });
            })
            .catch(error => {
                console.error('Error fetching media count:', error);
            });
    });
});
