window.addEventListener("DOMContentLoaded", () => {
  const mobileButton = document.createElement("button");
  mobileButton.innerText = "☰ เปิดเมนู";
  mobileButton.onclick = () => {
    const btn = document.querySelector(".md-header__button.md-icon");
    if (btn) btn.click();
  };
  mobileButton.className = "sidebar-toggle-header";

  const header = document.querySelector(".md-header__title");
  if (header) {
    header.parentNode.insertBefore(mobileButton, header.nextSibling);
  }
});
