// Adaugă clasa active la click
document.querySelectorAll('.navbar a').forEach(link => {
    link.addEventListener('click', function() {
        // Elimină clasa active de la toate link-urile
        document.querySelectorAll('.navbar a').forEach(l => l.classList.remove('active'));
        // Adaugă clasa active la link-ul apăsat
        this.classList.add('active');
    });
});