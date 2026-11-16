"""
PROYECTO 2 - FUNDAMENTOS DE INTELIGENCIA ARTIFICIAL
Archivo: evaluar.py

Ejecuta las 20 preguntas del informe contra el chatbot Prolog y contra el
chatbot LLM, y guarda las respuestas REALES en:
  - resultados_evaluacion.json
  - resultados_evaluacion.md   (tabla lista para pegar en el informe)

Uso:  python evaluar.py
"""

import json
import os
import time

from chatbot_llm import consultar_llm
from prolog_bridge import consultar_prolog

DIRECTORIO = os.path.dirname(os.path.abspath(__file__))
ARCHIVO_JSON = os.path.join(DIRECTORIO, "resultados_evaluacion.json")

PAUSA_ENTRE_LLM = 15      # segundos entre consultas al LLM (evita el limite de cuota)
ESPERA_SI_FALLA = 60      # segundos de espera antes de reintentar una pregunta fallida
INTENTOS_LLM = 3

# (tipo de pregunta, pregunta)
PREGUNTAS = [
    ("Lista de habitos", "¿Qué hábitos hay?"),
    ("Lista de categorias", "¿Qué categorías de hábitos existen?"),
    ("Habitos por categoria", "¿Qué hábitos son de descanso?"),
    ("Habitos por categoria", "¿Qué hábitos son de actividad física?"),
    ("Es saludable", "¿Es saludable beber agua?"),
    ("Beneficios", "¿Qué beneficios tiene hacer ejercicio?"),
    ("Beneficios", "Beneficios de dormir bien"),
    ("Frecuencia", "¿Cuántas veces al día debo cepillarme los dientes?"),
    ("Frecuencia", "¿Cuántas horas debo dormir?"),
    ("Frecuencia", "¿Cuánta agua debo tomar al día?"),
    ("Prevencion", "¿Qué previene lavarse las manos?"),
    ("Prevencion", "¿Qué hábitos ayudan a prevenir la caries?"),
    ("Habitos por beneficio", "¿Qué hábitos ayudan al bienestar general?"),
    ("Categoria de un habito", "¿A qué categoría pertenece caminar?"),
    ("Regla: relacionados", "¿Qué hábitos están relacionados con comer frutas?"),
    ("Regla: multiple", "¿Qué hábitos tienen más de un beneficio?"),
    ("Descripcion", "¿En qué consiste meditar?"),
    ("Fuera de la base", "¿Es saludable jugar videojuegos todo el día?"),
    ("Fuera de la base", "Para bajar de peso, ¿qué hábitos me recomiendas?"),
    ("Fuera de la base", "¿Sirve la vitamina C para prevenir el resfriado?"),
]


def ejecutar(funcion, pregunta):
    try:
        return funcion(pregunta)
    except RuntimeError as error:
        return f"[ERROR] {error}"


def llm_ok(texto):
    return not texto.startswith("[ERROR]")


def cargar_previos():
    """Resultados de una ejecucion anterior: sirven para no repetir lo que ya salio bien."""
    try:
        with open(ARCHIVO_JSON, encoding="utf-8") as f:
            return {r["pregunta"]: r for r in json.load(f)}
    except (OSError, ValueError, KeyError):
        return {}


def consultar_llm_con_paciencia(pregunta):
    respuesta = ""
    for intento in range(1, INTENTOS_LLM + 1):
        respuesta = ejecutar(consultar_llm, pregunta)
        if llm_ok(respuesta):
            break
        if intento < INTENTOS_LLM:
            print(f"    LLM fallo (intento {intento}); espero {ESPERA_SI_FALLA} s...")
            time.sleep(ESPERA_SI_FALLA)
    time.sleep(PAUSA_ENTRE_LLM)
    return respuesta


def celda(texto):
    """Formatea texto multilinea para una celda de tabla Markdown."""
    return texto.strip().replace("|", "\\|").replace("\n", "<br>")


def main():
    previos = cargar_previos()
    resultados = []
    for numero, (tipo, pregunta) in enumerate(PREGUNTAS, start=1):
        previo = previos.get(pregunta)
        if previo and llm_ok(previo["llm"]):
            print(f"[{numero}/{len(PREGUNTAS)}] {pregunta}  (LLM ya estaba bien, se conserva)")
            respuesta_llm = previo["llm"]
        else:
            print(f"[{numero}/{len(PREGUNTAS)}] {pregunta}")
            respuesta_llm = consultar_llm_con_paciencia(pregunta)
        resultados.append(
            {
                "n": numero,
                "tipo": tipo,
                "pregunta": pregunta,
                "prolog": ejecutar(consultar_prolog, pregunta),
                "llm": respuesta_llm,
            }
        )
        # Guarda el avance por si se interrumpe la ejecucion (conserva lo previo aun no procesado)
        pendientes = [previos[q] for _, q in PREGUNTAS[numero:] if q in previos]
        with open(ARCHIVO_JSON, "w", encoding="utf-8") as f:
            json.dump(resultados + pendientes, f, ensure_ascii=False, indent=2)

    fallidas = [r["n"] for r in resultados if not llm_ok(r["llm"])]
    if fallidas:
        print(f"\nAtencion: el LLM sigue fallando en las preguntas {fallidas}. "
              "Vuelva a ejecutar evaluar.py mas tarde: solo repetira esas.")

    lineas = [
        "| N° | Tipo | Pregunta | Respuesta Prolog | Respuesta LLM |",
        "|---|---|---|---|---|",
    ]
    for r in resultados:
        lineas.append(
            f"| {r['n']} | {r['tipo']} | {celda(r['pregunta'])} | "
            f"{celda(r['prolog'])} | {celda(r['llm'])} |"
        )
    with open(os.path.join(DIRECTORIO, "resultados_evaluacion.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(lineas) + "\n")

    print("\nListo: resultados_evaluacion.json y resultados_evaluacion.md")


if __name__ == "__main__":
    main()