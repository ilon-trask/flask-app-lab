document.addEventListener("DOMContentLoaded", () => {
  const flashes = document.querySelectorAll(".alert");
  flashes.forEach((flash) => {
    flash.dataset.enhanced = "true";
  });
});
