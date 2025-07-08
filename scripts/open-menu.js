function clickMenuManually(attempts = 20) {
  const isMobile = window.matchMedia("(max-width: 768px)").matches;
  const menuBtn = document.querySelector('.md-header__button.md-icon--menu');

  if (isMobile && menuBtn && menuBtn.offsetParent !== null) {
    console.log("✅ Clicked real menu button");
    menuBtn.click();
  } else if (attempts > 0) {
    console.log("⏳ Still waiting for menu button...");
    setTimeout(() => clickMenuManually(attempts - 1), 300);
  } else {
    console.warn("❌ Could not find menu button.");
  }
}

window.addEventListener('load', () => {
  clickMenuManually();
});
