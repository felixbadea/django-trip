// Adaugă clasa active la click
document.querySelectorAll('.navbar a').forEach(link => {
    link.addEventListener('click', function() {
        // Elimină clasa active de la toate link-urile
        document.querySelectorAll('.navbar a').forEach(l => l.classList.remove('active'));
        // Adaugă clasa active la link-ul apăsat
        this.classList.add('active');
    });
});

document.getElementById('contact-form').addEventListener('submit', function (event) {
    // Opțional: validare client-side
    const name = document.getElementById('name').value;
    const email = document.getElementById('email').value;
    const message = document.getElementById('message').value;
    if (!name || !email || !message) {
        event.preventDefault();
        alert('Vă rugăm să completați toate câmpurile!');
    }
});