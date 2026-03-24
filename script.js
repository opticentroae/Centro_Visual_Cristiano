// --- CONFIGURACIÓN DE VARIABLES ---
const galeria = document.getElementById("galeria");
const tituloElemento = document.getElementById("titulo-escrito");
const frase = "Cuidamos tu salud visual con la mejor tecnología";
let index = 0;
let borrando = false;
let datosInventario = [];

// 1. CARGA DE DATOS (Anti-Cache)
async function cargarDatos() {
  try {
    const respuesta = await fetch(`inventario.json?v=${Date.now()}`);
    datosInventario = await respuesta.json();
    cargarObras("todos");
  } catch (error) {
    console.error("Error en el motor de datos:", error);
  }
}

// 2. FILTRADO DE CATEGORÍAS
function filtrar(categoria, btn) {
  const botones = document.querySelectorAll(".filter-btn");
  botones.forEach((b) => b.classList.remove("active"));
  btn.classList.add("active");
  cargarObras(categoria);
}

// 3. RENDERIZADO DE CARTAS
function cargarObras(filtro = "todos") {
  if (!galeria) return;
  galeria.innerHTML = "";
  const fragmento = document.createDocumentFragment();

  const items =
    filtro.toLowerCase() === "todos"
      ? datosInventario
      : datosInventario.filter(
          (i) => i.cat.toLowerCase() === filtro.toLowerCase(),
        );

  items.forEach((item) => {
    const card = document.createElement("div");
    card.className = "card animar-subida";

    const esMulti = Array.isArray(item.nombre);
    const imgFrente = esMulti ? item.nombre[0] : item.nombre;
    const imgLado = esMulti && item.nombre[1] ? item.nombre[1] : null;
    const textoParaGrid =
      item.desc && item.desc.trim() !== ""
        ? item.desc
        : "Centro Visual Cristiano";

    card.innerHTML = `
            <div class="img-container ${imgLado ? "has-hover" : ""}">
                <img src="img/${imgFrente}.jpeg" class="img-main loader-target" alt="${imgFrente}" loading="lazy">
                ${imgLado ? `<img src="img/${imgLado}.jpeg" class="img-hover loader-target" alt="${imgLado}" loading="lazy">` : ""}
            </div>
            <span class="descripcion-viva">${textoParaGrid}</span>
        `;

    // Lógica de carga suave (Lazy Load)
    const imagenes = card.querySelectorAll(".loader-target");
    imagenes.forEach((img) => {
      if (img.complete) img.classList.add("loaded");
      else img.addEventListener("load", () => img.classList.add("loaded"));
    });

    card.onclick = () => abrirModal(imgFrente, item.desc);
    fragmento.appendChild(card);
  });

  galeria.appendChild(fragmento);
}

// 4. FUNCIONES DEL MODAL
function abrirModal(imagen, descripcion) {
  const modal = document.getElementById("modal-visor");
  const imgFull = document.getElementById("img-full");
  const descTxt = document.getElementById("desc-texto");

  imgFull.src = `img/${imagen}.jpeg`;
  descTxt.textContent = descripcion || "Calidad y estilo para tu visión.";
  modal.classList.add("active");
  document.body.classList.add("modal-open");
}

function cerrarModal() {
  document.getElementById("modal-visor").classList.remove("active");
  document.body.classList.remove("modal-open");
}

// 5. EFECTO ESCRITURA
function loopEscritura() {
  if (!tituloElemento) return;
  tituloElemento.textContent = frase.substring(0, index);

  let vel = borrando ? 50 : 120;
  if (!borrando && index === frase.length) {
    vel = 3000;
    borrando = true;
  } else if (borrando && index === 0) {
    borrando = false;
    vel = 1000;
  }
  index += borrando ? -1 : 1;
  setTimeout(loopEscritura, vel);
}

// 6. MANEJO DE SUCURSALES (Dropdown Adaptive)
function initSucursales() {
  const dropdownLinks = document.querySelectorAll(".has-dropdown > .cta-link");

  dropdownLinks.forEach((link) => {
    link.addEventListener("click", function (e) {
      // Solo aplicar comportamiento de clic en móviles (menor a 768px o 37.5em)
      if (window.innerWidth <= 600) {
        e.preventDefault();
        const parent = this.parentElement;

        // Si ya está activo, lo cerramos. Si no, cerramos otros y abrimos este.
        const isActive = parent.classList.contains("active");

        document.querySelectorAll(".nav-item").forEach((item) => {
          item.classList.remove("active");
        });

        if (!isActive) {
          parent.classList.add("active");
        }
      }
    });
  });

  // Cerrar si haces clic fuera del menú
  document.addEventListener("click", (e) => {
    if (!e.target.closest(".nav-item")) {
      document.querySelectorAll(".nav-item").forEach((item) => {
        item.classList.remove("active");
      });
    }
  });
}

// 7. DARK MODE TOGGLE (Mejorado)
function initTheme() {
  const themeBtn = document.getElementById("theme-toggle");
  const root = document.documentElement;

  // Al cargar, aplicamos lo que esté guardado
  const savedTheme = localStorage.getItem("theme") || "dark";
  root.setAttribute("data-theme", savedTheme);
  actualizarIcono(themeBtn, savedTheme);

  if (!themeBtn) return;

  themeBtn.onclick = () => {
    const isDark = root.getAttribute("data-theme") === "dark";
    const newTheme = isDark ? "light" : "dark";

    root.setAttribute("data-theme", newTheme);
    localStorage.setItem("theme", newTheme);
    actualizarIcono(themeBtn, newTheme);
  };
}

function actualizarIcono(btn, theme) {
  if (!btn) return;
  btn.innerHTML =
    theme === "dark"
      ? '<i class="fas fa-sun"></i>'
      : '<i class="fas fa-moon"></i>';
}

// 8. INICIALIZACIÓN GLOBAL
window.addEventListener("DOMContentLoaded", () => {
  cargarDatos();
  loopEscritura();
  initSucursales();
  initTheme();

  const btnCerrar = document.querySelector(".cerrar-modal");
  if (btnCerrar) btnCerrar.onclick = cerrarModal;

  window.onclick = (e) => {
    if (e.target.id === "modal-visor") cerrarModal();
  };
});

window.addEventListener("load", () => {
  const preloader = document.getElementById("preloader-art");
  if (preloader) {
    // 2500ms coincide con la animación 'load 2.5s' de tu CSS
    setTimeout(() => {
      preloader.style.opacity = "0";
      setTimeout(() => preloader.remove(), 500);
    }, 2500);
  }
});
