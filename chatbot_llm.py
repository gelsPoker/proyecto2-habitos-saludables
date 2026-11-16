"""
PROYECTO 2 - FUNDAMENTOS DE INTELIGENCIA ARTIFICIAL
Dominio: Habitos saludables
Archivo: chatbot_llm.py

Chatbot basado en un LLM. Usa como unica fuente de conocimiento la misma
base escrita en Prolog (conocimiento.pl), que se entrega al modelo como
contexto. No requiere librerias externas (solo biblioteca estandar).

Proveedores soportados (variable LLM_PROVIDER):
    anthropic (por defecto) -> ANTHROPIC_API_KEY
    openai                  -> OPENAI_API_KEY
    gemini                  -> GEMINI_API_KEY
Modelo opcional con LLM_MODEL. Las claves se leen del entorno o de un
archivo .env junto a este script (ver .env.example).

Uso en terminal:  python chatbot_llm.py
"""

import json
import os
import time
import urllib.error
import urllib.request

DIRECTORIO = os.path.dirname(os.path.abspath(__file__))
ARCHIVO_CONOCIMIENTO = os.path.join(DIRECTORIO, "conocimiento.pl")

MODELOS_POR_DEFECTO = {
    "anthropic": "claude-haiku-5-5",
    "openai": "gpt-4o-mini",
    "gemini": "gemini-2.0-flash",
}

INSTRUCCIONES = """Eres un chatbot que responde preguntas sobre habitos saludables.

Tu UNICA fuente de conocimiento es la siguiente base de conocimiento escrita en Prolog
(hechos y reglas). Reglas de comportamiento:
- Responde solo con informacion que se pueda obtener de la base, incluyendo lo que se
  deduzca de sus reglas (por ejemplo habitos_relacionados, se_complementan, habito_multiple).
- Si la pregunta no se puede responder con la base, dilo claramente: "No tengo esa
  informacion en mi base de conocimiento." No inventes datos ni uses conocimiento externo.
- Responde en espanol, de forma breve y clara, sin mostrar codigo Prolog.

BASE DE CONOCIMIENTO:
{conocimiento}
"""


# ------------------------------------------------------------
# Configuracion
# ------------------------------------------------------------

def cargar_env():
    """Carga variables desde un archivo .env (si existe) sin pisar el entorno."""
    ruta = os.path.join(DIRECTORIO, ".env")
    if not os.path.exists(ruta):
        return
    with open(ruta, encoding="utf-8") as archivo:
        for linea in archivo:
            linea = linea.strip()
            if not linea or linea.startswith("#") or "=" not in linea:
                continue
            clave, valor = linea.split("=", 1)
            os.environ.setdefault(clave.strip(), valor.strip().strip('"').strip("'"))


def cargar_conocimiento():
    """Lee el texto de la base de conocimiento Prolog."""
    with open(ARCHIVO_CONOCIMIENTO, encoding="utf-8") as archivo:
        return archivo.read()


def construir_instrucciones():
    return INSTRUCCIONES.replace("{conocimiento}", cargar_conocimiento())


# ------------------------------------------------------------
# Llamadas a cada proveedor (HTTP simple con urllib)
# ------------------------------------------------------------

def _post_json(url, cuerpo, cabeceras, intentos=4):
    """POST JSON con reintentos ante errores temporales (500, 502, 503, 504)."""
    for intento in range(1, intentos + 1):
        peticion = urllib.request.Request(
            url,
            data=json.dumps(cuerpo).encode("utf-8"),
            headers={"Content-Type": "application/json", **cabeceras},
            method="POST",
        )
        try:
            with urllib.request.urlopen(peticion, timeout=60) as respuesta:
                return json.loads(respuesta.read().decode("utf-8"))
        except urllib.error.HTTPError as error:
            detalle = error.read().decode("utf-8", errors="replace")[:300]
            if error.code in (500, 502, 503, 504) and intento < intentos:
                time.sleep(3 * intento)
                continue
            raise RuntimeError(f"Error HTTP {error.code} del proveedor: {detalle}") from error
        except urllib.error.URLError as error:
            raise RuntimeError(f"No se pudo conectar con el proveedor: {error.reason}") from error
        except TimeoutError as error:
            if intento < intentos:
                continue
            raise RuntimeError(
                "El proveedor tardo demasiado en responder tras varios intentos. "
                "Intente de nuevo mas tarde o pruebe otro modelo (LLM_MODEL)."
            ) from error


def _clave(nombre):
    valor = os.environ.get(nombre, "").strip()
    if not valor:
        raise RuntimeError(
            f"Falta la clave de API: defina {nombre} en el entorno o en el archivo .env"
        )
    return valor


def _anthropic(sistema, pregunta, modelo):
    datos = _post_json(
        "https://api.anthropic.com/v1/messages",
        {
            "model": modelo,
            "max_tokens": 500,
            "temperature": 0,
            "system": sistema,
            "messages": [{"role": "user", "content": pregunta}],
        },
        {"x-api-key": _clave("ANTHROPIC_API_KEY"), "anthropic-version": "2023-06-01"},
    )
    return "".join(b.get("text", "") for b in datos["content"] if b.get("type") == "text")


def _openai(sistema, pregunta, modelo):
    datos = _post_json(
        "https://api.openai.com/v1/chat/completions",
        {
            "model": modelo,
            "temperature": 0,
            "messages": [
                {"role": "system", "content": sistema},
                {"role": "user", "content": pregunta},
            ],
        },
        {"Authorization": "Bearer " + _clave("OPENAI_API_KEY")},
    )
    return datos["choices"][0]["message"]["content"]


def _gemini(sistema, pregunta, modelo):
    datos = _post_json(
        f"https://generativelanguage.googleapis.com/v1beta/models/{modelo}:generateContent",
        {
            "system_instruction": {"parts": [{"text": sistema}]},
            "contents": [{"role": "user", "parts": [{"text": pregunta}]}],
            "generationConfig": {"temperature": 0},
        },
        {"x-goog-api-key": _clave("GEMINI_API_KEY")},
    )
    return "".join(p.get("text", "") for p in datos["candidates"][0]["content"]["parts"])


PROVEEDORES = {"anthropic": _anthropic, "openai": _openai, "gemini": _gemini}


# ------------------------------------------------------------
# Interfaz publica
# ------------------------------------------------------------

def consultar_llm(pregunta):
    """Responde una pregunta usando el LLM y la base de conocimiento. Retorna texto."""
    cargar_env()
    proveedor = os.environ.get("LLM_PROVIDER", "anthropic").strip().lower()
    if proveedor not in PROVEEDORES:
        raise RuntimeError(
            f"LLM_PROVIDER '{proveedor}' no soportado. Use: {', '.join(PROVEEDORES)}"
        )
    modelo = os.environ.get("LLM_MODEL", "").strip() or MODELOS_POR_DEFECTO[proveedor]
    respuesta = PROVEEDORES[proveedor](construir_instrucciones(), pregunta, modelo)
    return respuesta.strip()


def main():
    print("Chatbot LLM de habitos saludables (escriba 'salir' para terminar)")
    while True:
        try:
            pregunta = input("\nPregunta: ").strip()
        except (EOFError, KeyboardInterrupt):
            break
        if pregunta.lower() in ("salir", "exit", "quit"):
            break
        if not pregunta:
            continue
        try:
            print(consultar_llm(pregunta))
        except RuntimeError as error:
            print("[error]", error)


if __name__ == "__main__":
    main()