document.addEventListener("DOMContentLoaded", function(){
    const searchInput = document.getElementById("search");

    // Coba deteksi apakah yang digunakan .row-content atau .card
    const rows = document.querySelectorAll(".row-content");
    const cards = document.querySelectorAll(".card");

    searchInput.addEventListener("keyup", function(){
        const query = searchInput.value.toLowerCase();

        // Kalau ada elemen .row-content (tabel style)
        if (rows.length > 0) {
            rows.forEach(row => {
                const cells = row.querySelectorAll(".detail");
                let rowText = "";
                cells.forEach(cell => {
                    rowText += cell.textContent.toLowerCase();
                });

                if(rowText.includes(query)){
                    row.style.display = "";
                }else{
                    row.style.display = "none";
                }
            });
        }

        // Kalau ada elemen .card (card style)
        if (cards.length > 0) {
            cards.forEach(card => {
                const content = card.querySelector(".card-content");
                const text = content.textContent.toLowerCase();

                if (text.includes(query)) {
                    card.style.display = "";
                } else {
                    card.style.display = "none";
                }
            });
        }
    });
});
