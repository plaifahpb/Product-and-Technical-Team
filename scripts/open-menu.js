function openSidebar(attempts = 20) {
  const isMobile = window.matchMedia("(max-width: 768px)").matches;
  const menuBtn = document.querySelector('[title="Toggle navigation"]');

  if (isMobile && menuBtn && menuBtn.offsetParent !== null) {
    console.log("✅ Sidebar menu found and clicked.");
    menuBtn.click();
  } else if (attempts > 0) {
    console.log("⏳ Waiting for sidebar menu button...");
    setTimeout(() => openSidebar(attempts - 1), 300);
  } else {
    console.warn("❌ Sidebar menu not found.");
  }
}

window.addEventListener("load", () => {
  openSidebar();
});
