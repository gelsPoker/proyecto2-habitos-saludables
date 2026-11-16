"""
PROYECTO 2 - FUNDAMENTOS DE INTELIGENCIA ARTIFICIAL
Archivo: prolog_bridge.py

Puente entre Python y el chatbot en Prolog: ejecuta SWI-Prolog como
subproceso, le entrega la pregunta por la entrada estandar y devuelve
lo que el chatbot escribe como respuesta.

Requiere SWI-Prolog instalado y accesible como "swipl" (o indicar la ruta
completa en la variable de entorno SWIPL_PATH).
"""

import os
import subprocess
import unicodedata

DIRECTORIO = os.path.dirname(os.path.abspath(__file__))


def quitar_tildes(texto):
    """Elimina tildes y dieresis (la base Prolog trabaja con texto sin tildes)."""
    descompuesto = unicodedata.normalize("NFD", texto)
    return "".join(c for c in descompuesto if unicodedata.category(c) != "Mn")


def consultar_prolog(pregunta, tiempo_maximo=15):
    """Envia la pregunta al chatbot Prolog y retorna su respuesta como texto."""
    ejecutable = os.environ.get("SWIPL_PATH", "swipl")
    pregunta = quitar_tildes(" ".join(pregunta.split()))
    comando = [ejecutable, "-q", "-g", "consulta_web", "-t", "halt", "chatbot.pl"]
    try:
        resultado = subprocess.run(
            comando,
            input=pregunta + "\n",
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=tiempo_maximo,
            cwd=DIRECTORIO,
        )
    except FileNotFoundError as error:
        raise RuntimeError(
            "No se encontro SWI-Prolog. Instalelo o defina SWIPL_PATH con la ruta de swipl."
        ) from error
    except subprocess.TimeoutExpired as error:
        raise RuntimeError("El chatbot Prolog tardo demasiado en responder.") from error

    respuesta = resultado.stdout.strip()
    if resultado.returncode != 0 and not respuesta:
        raise RuntimeError("Error en Prolog: " + resultado.stderr.strip()[:300])
    return respuesta or "(El chatbot Prolog no entrego respuesta.)"


if __name__ == "__main__":
    import sys

    print(consultar_prolog(" ".join(sys.argv[1:]) or "que habitos hay"))
