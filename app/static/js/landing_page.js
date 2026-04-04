// Add event listener to form submission
document.addEventListener("DOMContentLoaded", function() {
    const form = document.querySelector("form");
    form.addEventListener("submit", function(event) {
        // Prevent default form submission
        event.preventDefault();
        // Send form data to server
        fetch("/contact-form", {
            method: "POST",
            headers: {
                "Content-Type": "application/x-www-form-urlencoded"
            },
            body: new URLSearchParams({
                name: document.querySelector("#name").value,
                email: document.querySelector("#email").value,
                message: document.querySelector("#message").value
            })
        })
        .then(response => response.json())
        .then(data => console.log(data))
        .catch(error => console.error(error));
    });
});
