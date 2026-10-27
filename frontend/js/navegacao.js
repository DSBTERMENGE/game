const botaoVoltar = document.querySelector("#botao-voltar");

if (botaoVoltar) {
  const destinoAlternativo = botaoVoltar.dataset.destinoVoltar;
  botaoVoltar.disabled = !destinoAlternativo && window.history.length <= 1;
  botaoVoltar.addEventListener("click", () => {
    if (window.history.length > 1) window.history.back();
    else if (destinoAlternativo) window.location.assign(destinoAlternativo);
  });
}

document.querySelectorAll(".navegacao-menu").forEach((menu) => {
  menu.addEventListener("toggle", () => {
    if (!menu.open) return;
    document.querySelectorAll(".navegacao-menu[open]").forEach((outro) => {
      if (outro !== menu) outro.removeAttribute("open");
    });
  });
});
