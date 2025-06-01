document.addEventListener('DOMContentLoaded', function () {
    const faqIcon = document.getElementById('faq-icon');
    const faqPopup = document.getElementById('faq-popup');
    const faqClose = document.getElementById('faq-close');

    faqIcon.addEventListener('click', function () {
        faqPopup.style.display = 'flex';
    });

    faqClose.addEventListener('click', function () {
        faqPopup.style.display = 'none';
    });

    window.addEventListener('click', function (e) {
        if (e.target === faqPopup) {
            faqPopup.style.display = 'none';
        }
    });
});
