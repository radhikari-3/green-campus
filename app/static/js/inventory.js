document.addEventListener("DOMContentLoaded", function () {
    const toggle = document.getElementById("viewToggle");
    const icon = document.getElementById("viewIcon");
    const listView = document.querySelector('[view="table"]');
    const cardView = document.querySelector('[view="card"]');

    toggle.addEventListener("change", () => {
        const isCardView = toggle.checked;
        listView.classList.toggle("d-none", isCardView);
        cardView.classList.toggle("d-none", !isCardView);

        icon.classList.toggle("bi-list", !isCardView);
        icon.classList.toggle("bi-grid", isCardView);
    });
});
