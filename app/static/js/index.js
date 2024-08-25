// Pegar os elementos do DOM
var modal = document.getElementById("signupModal");
var btn = document.getElementById("openSignupModal");
var btn2 = document.getElementById("openSignupModal2");
var span = document.getElementById("closeSignupModal");

// Quando o usuário clicar no botão, abrir o modal
btn.onclick = function() {
    modal.style.display = "block";
}
btn2.onclick = function() {
    modal.style.display = "block";
}

// Quando o usuário clicar no X (span), fechar o modal
span.onclick = function() {
    modal.style.display = "none";
}

// Quando o usuário clicar fora do modal, fechar o modal
window.onclick = function(event) {
    if (event.target == modal) {
        modal.style.display = "none";
    }
}