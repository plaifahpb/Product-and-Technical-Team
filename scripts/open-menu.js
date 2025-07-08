function waitForMenuButtonAndClick(attempts = 20) {
  const isMobile = window.matchMedia("(max-width: 768px)").matches;
  const menuBtn = document.querySelector('.md-header__button.md-icon--menu');

  if (isMobile && menuBtn) {
    console.log("✅ Found menu button, opening...");
    menuBtn.click();
  } else if (attempts > 0) {
    requestAnimationFrame(() => waitForMenuButtonAndClick(attempts - 1));
  } else {
    console.warn("⚠️ Menu button not found after multiple attempts.");
  }
}

window.addEventListener('load', () => {
  waitForMenuButtonAndClick();
});



