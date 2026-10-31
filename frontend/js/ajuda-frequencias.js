const botaoAbrir = document.querySelector("#botao-ajuda-frequencias");
const dialogo = document.querySelector("#dialogo-ajuda-frequencias");

if (botaoAbrir && dialogo) {
  botaoAbrir.addEventListener("click", () => dialogo.showModal());
  dialogo.addEventListener("click", (evento) => {
    if (evento.target === dialogo) dialogo.close();
  });
}
