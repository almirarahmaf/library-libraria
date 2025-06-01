// base user
document.addEventListener("DOMContentLoaded", function () {
    const toggle = document.getElementById("categoriToggle");
    const menu = document.getElementById("categoriMenu");
    const icon = document.getElementById("categoriIcon");
    const bookBtn = document.getElementById("book");
    const shelf = document.getElementById("borrowingShelf");
    const closeShelf = document.getElementById("closeShelf");

    // Toggle kategori dropdown
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

    // Toggle borrowing shelf
    bookBtn.addEventListener("click", function (e) {
        e.preventDefault(); // Supaya tidak reload halaman
        shelf.classList.remove("d-none");
    });

    // Close shelf
    closeShelf.addEventListener("click", function () {
        shelf.classList.add("d-none");
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
function togglePasswordVisibility(fieldId, iconId) {
    const passwordField = document.getElementById(fieldId);
    const toggleIcon = document.getElementById(iconId);

    if (passwordField.type === 'password') {
        passwordField.type = 'text';
        toggleIcon.classList.remove('fa-eye');
        toggleIcon.classList.add('fa-eye-slash');
    } else {
        passwordField.type = 'password';
        toggleIcon.classList.remove('fa-eye-slash');
        toggleIcon.classList.add('fa-eye');
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

// verification code
document.addEventListener("DOMContentLoaded", function () {
    const inputs = document.getElementById("inputs");

    inputs.addEventListener("input", function(event) {
        const target = event.target;
        const val = target.value;

        if (isNaN(val)) {
            target.value = "";
            return;
        }

        if (val != "") {
            const next = target.nextElementSibling;
            if (next) {
                next.focus();
            }
        }
    });

    inputs.addEventListener("keyup", function(event) {
        const target = event.target;
        const key = event.key.toLowerCase();

        if (key == "backspace" || key == "delete") {
            target.value = "";
            const prev = target.previousElementSibling;
            if (prev) {
                prev.focus();
            }
            return;
        }
    });

    // resend otp timer
    var timeleft = 60;

    var downloadTimer = setInterval(function(){
        timeleft--;
        document.getElementById("countdowntimer").textContent = timeleft;
        var resendOtpElement = document.getElementById("resendotp");

        if(timeleft < 0) {
            clearInterval(downloadTimer);
            document.getElementById("countdown").hidden = true;
            resendOtpElement.classList.remove("hidden");
        }
    }, 1000);
});