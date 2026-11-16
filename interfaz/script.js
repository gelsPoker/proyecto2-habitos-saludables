// ============================================================
// PROYECTO 2 - FUNDAMENTOS DE INTELIGENCIA ARTIFICIAL
// Interfaz del chatbot de habitos saludables
// Archivo: script.js
// ============================================================


// Elementos de la interfaz
const formulario = document.getElementById("formulario");
const pregunta = document.getElementById("pregunta");
const chat = document.getElementById("chat");


// Evento que se ejecuta al enviar el formulario
formulario.addEventListener("submit", function (evento) {

    // Evita que la pagina se recargue
    evento.preventDefault();

    // Obtiene la pregunta escrita por el usuario
    const textoPregunta = pregunta.value.trim();

    // Verifica que exista texto
    if (textoPregunta === "") {
        return;
    }

    // Muestra la pregunta en el chat
    agregarMensaje(textoPregunta, "usuario");

    // Limpia el campo de texto
    pregunta.value = "";

    // Vuelve a seleccionar el campo para escribir
    pregunta.focus();
});


// Funcion para agregar un mensaje a la conversacion
function agregarMensaje(texto, tipo) {

    const mensaje = document.createElement("div");
    mensaje.classList.add("mensaje", tipo);

    const contenido = document.createElement("p");
    contenido.textContent = texto;

    mensaje.appendChild(contenido);
    chat.appendChild(mensaje);

    // Desplaza el chat hacia el ultimo mensaje
    chat.scrollTop = chat.scrollHeight;
}