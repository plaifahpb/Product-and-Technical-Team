window.addEventListener('load', () => {
  const isMobile = window.matchMedia("(max-width: 768px)").matches;
  const menuBtn = document.querySelector(".md-header__button.md-icon--menu");
  if (isMobile && menuBtn) {
    menuBtn.click();
  }
});
