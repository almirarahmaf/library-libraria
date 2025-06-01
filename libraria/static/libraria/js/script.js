// base user
document.addEventListener("DOMContentLoaded", function () {
    const toggle = document.getElementById("categoriToggle");
    const menu = document.getElementById("categoriMenu");
    const icon = document.getElementById("categoriIcon");

    toggle.addEventListener("click", function () {
        menu.classList.toggle("d-none");
        icon.classList.toggle("fa-chevron-down");
        icon.classList.toggle("fa-chevron-up");
    });

    document.addEventListener("click", function (e) {
        if (!toggle.contains(e.target) && !menu.contains(e.target)) {
            menu.classList.add("d-none");
            icon.classList.add("fa-chevron-down");
            icon.classList.remove("fa-chevron-up");
        }
    });
});

document.addEventListener('DOMContentLoaded', function () {
    const shelfPanel = document.getElementById('borrowingShelf');
    const openBtn = document.getElementById('book'); 
    const closeBtn = document.getElementById('closeShelf');

    // Buka panel saat klik tombol book
    openBtn.addEventListener('click', function (e) {
        e.preventDefault();
        shelfPanel.classList.remove('d-none');
        e.stopPropagation(); 
    });

    // Tutup panel saat klik tombol close
    closeBtn.addEventListener('click', function () {
        shelfPanel.classList.add('d-none');
    });

    // Deteksi klik di luar panel dan tombol book (termasuk gambarnya)
    document.addEventListener('click', function (e) {
        const isClickInsideShelf = shelfPanel.contains(e.target);
        const isClickOnBookBtn = openBtn.contains(e.target); 

        if (!isClickInsideShelf && !isClickOnBookBtn) {
            shelfPanel.classList.add('d-none');
        }
    });
});



// login
function togglePasswordVisibility(element) {
    const input = element.previousElementSibling;
    const icon = element.querySelector("i");

    if (input.type === "password") {
        input.type = "text";
        icon.classList.remove("fa-eye");
        icon.classList.add("fa-eye-slash");
    } else {
        input.type = "password";
        icon.classList.remove("fa-eye-slash");
        icon.classList.add("fa-eye");
    }
}


// validasi new password dan confirm password
function validatePasswords(fieldPassword, fieldConfirmPassword) {
    const newPassword = document.getElementById(fieldPassword).value;
    const confirmPassword = document.getElementById(fieldConfirmPassword).value;

    if (newPassword !== confirmPassword) {
        alert('Passwords do not match! Please try again.');
        return false;
    }
    return true;
}