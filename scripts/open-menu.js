function clickDrawerButton(attempts = 20) {
  const isMobile = window.matchMedia("(max-width: 768px)").matches;
  const menuBtn = document.querySelector('button[data-md-toggle="drawer"]');

  if (isMobile && menuBtn && menuBtn.offsetParent !== null) {
    console.log("✅ Found drawer button → clicking...");
    menuBtn.click();
  } else if (attempts > 0) {
    console.log("⏳ Retrying to find drawer button...");
    setTimeout(() => clickDrawerButton(attempts - 1), 300);  // ✅ ใช้ arrow function แทน string
  } else {
    console.warn("❌ Drawer button not found after multiple retries.");
  }
}

window.addEventListener('load', () => {
  clickDrawerButton();
});
