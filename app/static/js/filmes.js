document.addEventListener('DOMContentLoaded', function() {
    const cards = document.querySelectorAll('.card-filme');

    cards.forEach(card => {
        card.addEventListener('click', function() {
            const id = this.getAttribute('data-id');
            window.location.href = `/filme/${id}`;
            console.log(`Clicou no filme com id: ${id}`)
        });
    });
});