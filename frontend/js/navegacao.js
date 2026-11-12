document.querySelectorAll(".navegacao-menu").forEach((menu) => {
  menu.addEventListener("toggle", () => {
    if (!menu.open) return;
    document.querySelectorAll(".navegacao-menu[open]").forEach((outro) => {
      if (outro !== menu) outro.removeAttribute("open");
    });
  });
});
