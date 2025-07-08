window.addEventListener('DOMContentLoaded', () => {
  const isMobile = window.matchMedia("(max-width: 768px)").matches;
  const menuBtn = document.querySelector('.md-header__button.md-icon--menu');
  if (isMobile && menuBtn) {
    setTimeout(() => menuBtn.click(), 500);  // รอให้โหลดเมนูเสร็จแล้วค่อยคลิก
  }
});

