function validatePasskey(event) {
    event.preventDefault(); // Prevent form submission

    const passkey = document.getElementById('passkey').value;
    const errorMessage = document.getElementById('error-message');
    const correctPasskey = "admin@123"; // Change as needed

    if (passkey !== correctPasskey) {
        errorMessage.style.display = 'block';
    } else {
        errorMessage.style.display = 'none';
        window.location.href = "/librarian_operations";
    }
}