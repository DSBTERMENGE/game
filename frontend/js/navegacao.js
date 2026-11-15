const menusNavegacao = [...document.querySelectorAll(".navegacao-menu")];

function posicionarMenu(menu) {
  const resumo = menu.querySelector("summary");
  const painel = menu.querySelector("nav");
  if (!resumo || !painel) return;
  const ancora = resumo.getBoundingClientRect();
  const largura = Math.max(painel.offsetWidth, 208);
  const margem = 8;
  const esquerda = Math.min(
    Math.max(margem, ancora.left),
    Math.max(margem, window.innerWidth - largura - margem),
  );
  menu.style.setProperty("--navegacao-menu-top", `${ancora.bottom + 3}px`);
  menu.style.setProperty("--navegacao-menu-left", `${esquerda}px`);
}

menusNavegacao.forEach((menu) => {
  menu.addEventListener("toggle", () => {
    if (!menu.open) return;
    menusNavegacao.forEach((outro) => {
      if (outro !== menu) outro.removeAttribute("open");
    });
    posicionarMenu(menu);
  });
});

window.addEventListener("resize", () => {
  menusNavegacao.filter((menu) => menu.open).forEach(posicionarMenu);
});

document.querySelector(".barra-navegacao")?.addEventListener("scroll", () => {
  menusNavegacao.filter((menu) => menu.open).forEach(posicionarMenu);
});
