document.addEventListener("DOMContentLoaded", function() {
    const form = document.getElementById("myForm");
    form.addEventListener("submit", function(event) {
        const username = document.getElementById("username").value;
        const email = document.getElementById("email").value;
        
        if (username === "" || email === "") {
            alert("Username and Email are required!");
            event.preventDefault(); // Prevent form submission
        }
    });
});