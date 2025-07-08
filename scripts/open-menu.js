function waitForMenuAndClick(retries = 20) {
  const isMobile = window.matchMedia("(max-width: 768px)").matches;
  const menuBtn = document.querySelector('.md-header__button.md-icon--menu');

  if (isMobile && menuBtn && menuBtn.offsetParent !== null) {
    console.log("✅ Menu button found and visible → Clicked");
    menuBtn.click();
  } else if (retries > 0) {
    console.log("⏳ Waiting for menu button...");
    setTimeout(() => waitForMenuAndClick(retries - 1), 300); // wait and retry
  } else {
    console.warn("❌ Menu button not found after multiple tries.");
  }
}

window.addEventListener("load", () => {
  waitForMenuAndClick();
});
