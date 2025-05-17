document.addEventListener('DOMContentLoaded', function () {
    var videoModal = document.getElementById('videoModal');
    videoModal.addEventListener('show.bs.modal', function (event) {
        var button = event.relatedTarget; // Imaginea care a declanșat modalul
        var videoUrl = button.getAttribute('data-video-url');
        var cityName = button.querySelector('img').getAttribute('alt');
        var iframe = videoModal.querySelector('#videoIframe');
        var modalTitle = videoModal.querySelector('.modal-title');

        iframe.src = videoUrl; // Setează sursa videoclipului
        modalTitle.textContent = cityName + ' Video'; // Actualizează titlul
    });

    videoModal.addEventListener('hidden.bs.modal', function () {
        var iframe = videoModal.querySelector('#videoIframe');
        iframe.src = ''; // Resetează sursa pentru a opri videoclipul
    });
});