window.addEventListener("DOMContentLoaded", () => {
  const mobileButton = document.createElement("button");
  mobileButton.innerHTML = "&#9776;"; // HTML entity for ☰
  mobileButton.className = "sidebar-toggle-icon";
  mobileButton.setAttribute("aria-label", "Toggle menu");
  mobileButton.onclick = () => {
    const btn = document.querySelector(".md-header__button.md-icon");
    if (btn) btn.click();
  };

  const headerActions = document.querySelector(".md-header__title");
  if (headerActions) {
    headerActions.parentNode.insertBefore(mobileButton, headerActions.nextSibling);
  }
});
