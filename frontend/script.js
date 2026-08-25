const API_URL = "http://localhost:5000/api/eventos";
let todosLosEventos = [];
let categoriaActiva = "todos";
let fechaActiva = "todas";
let textoBusqueda = "";

async function cargarEventos() {
  try {
    const respuesta = await fetch(API_URL);
    todosLosEventos = await respuesta.json();
    armarPestanasDeFecha();
    aplicarFiltros();
  } catch (error) {
    document.getElementById("eventos").innerHTML =
      "<p id='estado'>Error al cargar los eventos. ¿Está prendido el servidor (app.py)?</p>";
    console.error(error);
  }
}

// Arma los botones LUN 24 / MAR 25... a partir de las fechas que existen en los eventos
function armarPestanasDeFecha() {
  const contenedor = document.getElementById("dias");

  // Sacamos las fechas únicas (solo el día, sin hora) y las ordenamos
  const fechasUnicas = [...new Set(
    todosLosEventos
      .filter(ev => ev.fecha_hora)
      .map(ev => ev.fecha_hora.slice(0, 10)) // "2026-09-11"
  )].sort();

  contenedor.innerHTML = `<button class="dia activo" data-fecha="todas">Todas</button>`;

  fechasUnicas.forEach(fechaISO => {
    const fecha = new Date(fechaISO + "T00:00:00");
    const diaSemana = fecha.toLocaleDateString("es-AR", { weekday: "short" }).toUpperCase().replace(".", "");
    const diaNumero = fecha.getDate();

    const boton = document.createElement("button");
    boton.className = "dia";
    boton.dataset.fecha = fechaISO;
    boton.innerHTML = `<span class="dia-nombre">${diaSemana}</span><span class="dia-numero">${diaNumero}</span>`;
    contenedor.appendChild(boton);
  });
}

function aplicarFiltros() {
  let eventos = todosLosEventos;

  if (categoriaActiva !== "todos") {
    eventos = eventos.filter(ev => ev.categoria === categoriaActiva);
  }
  if (fechaActiva !== "todas") {
    eventos = eventos.filter(ev => ev.fecha_hora && ev.fecha_hora.slice(0, 10) === fechaActiva);
  }
  if (textoBusqueda.trim() !== "") {
    const texto = textoBusqueda.toLowerCase();
    eventos = eventos.filter(ev => ev.titulo.toLowerCase().includes(texto));
  }

  renderizarEventos(eventos);
    lucide.createIcons();
}

function renderizarEventos(eventos) {
  const contenedor = document.getElementById("eventos");

  if (eventos.length === 0) {
    contenedor.innerHTML = "<p id='estado'>No hay eventos para este filtro.</p>";
    return;
  }

  // Agrupar eventos por fecha (solo el día, sin hora)
  const grupos = {};
  eventos.forEach(ev => {
    const clave = ev.fecha_hora ? ev.fecha_hora.slice(0, 10) : "sin-fecha";
    if (!grupos[clave]) grupos[clave] = [];
    grupos[clave].push(ev);
  });

  // Ordenar las claves de fecha (las que no tienen fecha van al final)
  const clavesOrdenadas = Object.keys(grupos).sort((a, b) => {
    if (a === "sin-fecha") return 1;
    if (b === "sin-fecha") return -1;
    return a.localeCompare(b);
  });

  contenedor.innerHTML = "";

  clavesOrdenadas.forEach(clave => {
    const tituloGrupo = clave === "sin-fecha"
      ? "Fecha a confirmar"
      : new Date(clave + "T00:00:00").toLocaleDateString("es-AR", {
          weekday: "long", day: "numeric", month: "long"
        });

    const cantidad = grupos[clave].length;
    const textoCantidad = cantidad === 1 ? "1 evento" : `${cantidad} eventos`;

    const seccion = document.createElement("div");
    seccion.className = "grupo-dia";
    seccion.innerHTML = `
      <div class="grupo-header">
          <span><i data-lucide="calendar"></i> ${tituloGrupo}</span>
        <span class="grupo-cantidad">${textoCantidad}</span>
      </div>
      <div class="grupo-eventos"></div>
    `;

    const contenedorTarjetas = seccion.querySelector(".grupo-eventos");

    grupos[clave].forEach(ev => {
      const hora = ev.fecha_hora
        ? new Date(ev.fecha_hora).toLocaleTimeString("es-AR", { hour: "2-digit", minute: "2-digit" })
        : "Hora a confirmar";

      const div = document.createElement("div");
      div.className = "evento";
      div.innerHTML = `
        <span class="categoria-tag">${ev.categoria || "Evento"}</span>
        <h2>${ev.titulo}</h2>
        <div class="evento-datos">
          <div class="dato"><i data-lucide="clock"></i> <span>${hora}</span></div>
          <div class="dato"><i data-lucide="map-pin"></i> <span>${ev.lugar || "Lugar a confirmar"}</span></div>
          ${ev.precio ? `<div class="dato precio"><i data-lucide="banknote"></i> <span>${ev.precio}</span></div>` : ""}
        </div>
        <a href="${ev.link_fuente}" target="_blank">Ir a la página →</a>
      `;
      contenedorTarjetas.appendChild(div);
    });

    contenedor.appendChild(seccion);
  });
}

// Click en categorías (Todos / Teatro / Música / Fiestas)
document.getElementById("categorias").addEventListener("click", (e) => {
  if (e.target.tagName !== "BUTTON") return;
  document.querySelectorAll("#categorias button").forEach(b => b.classList.remove("activo"));
  e.target.classList.add("activo");
  categoriaActiva = e.target.dataset.categoria;
  aplicarFiltros();
});

// Click en días (delegado, porque los botones se crean dinámicamente)
document.getElementById("dias").addEventListener("click", (e) => {
  const boton = e.target.closest("button");
  if (!boton) return;
  document.querySelectorAll("#dias button").forEach(b => b.classList.remove("activo"));
  boton.classList.add("activo");
  fechaActiva = boton.dataset.fecha;
  aplicarFiltros();
});

document.getElementById("btn-buscar").addEventListener("click", () => {
  textoBusqueda = document.getElementById("busqueda").value;
  aplicarFiltros();
});

document.getElementById("busqueda").addEventListener("keydown", (e) => {
  if (e.key === "Enter") {
    textoBusqueda = document.getElementById("busqueda").value;
    aplicarFiltros();
  }
});

cargarEventos();     