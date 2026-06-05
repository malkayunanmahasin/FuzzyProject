// ==========================
// SLIDER VALUE UPDATE
// ==========================
const bb = document.getElementById("bb");
const tb = document.getElementById("tb");
const umur = document.getElementById("umur");

const bbVal = document.getElementById("bbVal");
const tbVal = document.getElementById("tbVal");
const umurVal = document.getElementById("umurVal");

// cek biar ga error kalau element ga ada di halaman lain
if (bb && bbVal) {
  bb.addEventListener("input", () => {
    bbVal.innerText = bb.value;

    // efek glow dikit
    bb.style.transform = "scale(1.02)";
    setTimeout(() => (bb.style.transform = "scale(1)"), 150);
  });
}

if (tb && tbVal) {
  tb.addEventListener("input", () => {
    tbVal.innerText = tb.value;

    tb.style.transform = "scale(1.02)";
    setTimeout(() => (tb.style.transform = "scale(1)"), 150);
  });
}

if (umur && umurVal) {
  umur.addEventListener("input", () => {
    umurVal.innerText = umur.value;

    umur.style.transform = "scale(1.02)";
    setTimeout(() => (umur.style.transform = "scale(1)"), 150);
  });
}


// ==========================
// ACCORDION (LEARN PAGE)
// ==========================
const items = document.querySelectorAll(".accordion-item");

if (items.length > 0) {
  items.forEach((item) => {
    item.addEventListener("click", () => {

      items.forEach((other) => {
        if (other !== item) {
          other.classList.remove("active");
        }
      });

      item.classList.toggle("active");
    });
  });
}


// ==========================
// ANIMASI SELECT (INPUT PAGE)
// ==========================
const selects = document.querySelectorAll("select");

selects.forEach((select) => {
  select.addEventListener("change", () => {
    select.style.transform = "scale(1.03)";
    select.style.boxShadow = "0 0 20px rgba(34,211,238,.3)";

    setTimeout(() => {
      select.style.transform = "scale(1)";
      select.style.boxShadow = "none";
    }, 200);
  });
});