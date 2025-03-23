document.addEventListener("DOMContentLoaded", function () {
    const profileIcon = document.getElementById("profileIcon");
    const dropdownMenu = document.getElementById("dropdownMenu");

    profileIcon.addEventListener("click", function (event) {
        dropdownMenu.style.display = dropdownMenu.style.display === "block" ? "none" : "block";
        event.stopPropagation();
    });

    // Close dropdown if clicked outside
    document.addEventListener("click", function (event) {
        if (!profileIcon.contains(event.target) && !dropdownMenu.contains(event.target)) {
            dropdownMenu.style.display = "none";
        }
    });
});
