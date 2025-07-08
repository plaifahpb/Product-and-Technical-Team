function waitAndClickMenu(retries = 20) {
  const isMobile = window.matchMedia("(max-width: 768px)").matches;
  const allMenuButtons = document.querySelectorAll('button, .md-header__button, .md-icon--menu');

  for (const btn of allMenuButtons) {
    const isMenuIcon = btn?.ariaLabel?.toLowerCase().includes('menu') || btn?.className?.includes('menu');
    const isVisible = btn && btn.offsetParent !== null;
    if (isMobile && isMenuIcon && isVisible) {
      console.log("✅ Clicked menu via fallback method");
      btn.click();
      return;
    }
  }

  if (retries > 0) {
    console.log("⏳ Retrying to find menu button...");
    setTimeout(() => waitAndClickMenu(retries - 1), 300);
  } else {
    console.warn("❌ Menu button not found.");
  }
}

window.addEventListener("load", () => {
  waitAndClickMenu();
});
