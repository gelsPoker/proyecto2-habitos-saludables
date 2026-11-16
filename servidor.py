"""
PROYECTO 2 - FUNDAMENTOS DE INTELIGENCIA ARTIFICIAL
Archivo: servidor.py

Servidor web simple (solo biblioteca estandar) que:
  - entrega la interfaz web (carpeta interfaz/)
  - expone POST /api/chat con {"pregunta": "...", "modo": "prolog|llm|ambos"}

Uso:  python servidor.py     y abrir http://localhost:8000
"""

import json
import os
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer

from chatbot_llm import consultar_llm
from prolog_bridge import consultar_prolog

DIRECTORIO = os.path.dirname(os.path.abspath(__file__))
CARPETA_INTERFAZ = os.path.join(DIRECTORIO, "interfaz")
PUERTO = int(os.environ.get("PORT", "8000"))
MODOS = {"prolog", "llm", "ambos"}


def responder(pregunta, modo):
    """Consulta el/los chatbots segun el modo. Un fallo en uno no afecta al otro."""
    salida = {}
    for nombre, funcion in (("prolog", consultar_prolog), ("llm", consultar_llm)):
        if modo not in (nombre, "ambos"):
            continue
        try:
            salida[nombre] = {"ok": True, "texto": funcion(pregunta)}
        except RuntimeError as error:
            salida[nombre] = {"ok": False, "texto": str(error)}
    return salida


class Manejador(SimpleHTTPRequestHandler):
    def do_POST(self):
        if self.path != "/api/chat":
            self.send_error(404)
            return
        try:
            largo = int(self.headers.get("Content-Length", 0))
            datos = json.loads(self.rfile.read(largo).decode("utf-8"))
            pregunta = str(datos.get("pregunta", "")).strip()
            modo = datos.get("modo", "prolog")
        except (ValueError, UnicodeDecodeError):
            self._json(400, {"error": "Solicitud invalida"})
            return
        if not pregunta or len(pregunta) > 500 or modo not in MODOS:
            self._json(400, {"error": "Pregunta vacia, muy larga o modo invalido"})
            return
        self._json(200, responder(pregunta, modo))

    def _json(self, codigo, contenido):
        cuerpo = json.dumps(contenido, ensure_ascii=False).encode("utf-8")
        self.send_response(codigo)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(cuerpo)))
        self.end_headers()
        self.wfile.write(cuerpo)


def main():
    manejador = partial(Manejador, directory=CARPETA_INTERFAZ)
    servidor = ThreadingHTTPServer(("127.0.0.1", PUERTO), manejador)
    print(f"Chatbot disponible en http://localhost:{PUERTO}  (Ctrl+C para detener)")
    try:
        servidor.serve_forever()
    except KeyboardInterrupt:
        print("\nServidor detenido.")


if __name__ == "__main__":
    main()
