# Chatbot de Hábitos Saludables — Proyecto 2 (Fundamentos de IA)

Chatbot en dos versiones sobre la misma base de conocimiento: **Prolog** (lógica de primer orden) y **LLM** (Python), con interfaz web.

## Requisitos
- [SWI-Prolog](https://www.swi-prolog.org/) (`swipl` en el PATH, o variable `SWIPL_PATH`)
- Python 3.8+ (sin librerías externas)
- Clave de API de un proveedor de LLM (solo para la versión LLM)

## Configuración del LLM
Copie `.env.example` como `.env`, elija `LLM_PROVIDER` (`anthropic`, `openai` o `gemini`) y complete la clave correspondiente. Si el nombre de modelo por defecto ya no existe, defina `LLM_MODEL`.

## Uso
| Qué | Comando |
|---|---|
| Chatbot Prolog en terminal (menú) | `swipl chatbot.pl` y luego `iniciar.` |
| Chatbot LLM en terminal | `python chatbot_llm.py` |
| Interfaz web (Prolog, LLM o ambos) | `python servidor.py` → http://localhost:8000 |
| Evaluación con las 20 preguntas | `python evaluar.py` → `resultados_evaluacion.md/.json` |

## Cómo modificar el conocimiento (útil para la interrogación)
Todo el conocimiento vive en `conocimiento.pl`. Para agregar un hábito nuevo, por ejemplo `tomar_sol`:

```prolog
habito(tomar_sol).
categoria(tomar_sol, actividad_fisica).
beneficia(tomar_sol, bienestar_general).
descripcion(tomar_sol, "Consiste en exponerse al sol con proteccion.").
frecuencia(tomar_sol, "Unos minutos al dia, con proteccion solar.").
previene(tomar_sol, fatiga).
```

Y en `chatbot.pl` (para que el chatbot Prolog lo nombre en las respuestas):

```prolog
nombre_habito(tomar_sol, "tomar sol").
alias_habito(tomar_sol, "sol").          % opcional
```

- **Nueva categoría:** usarla en `categoria/2` y agregar `nombre_categoria(id, "texto")` en `chatbot.pl`.
- **Nuevo beneficio:** usarlo en `beneficia/2` y agregar `nombre_beneficio(id, "texto")` en `chatbot.pl`.
- **Nuevo problema que se previene:** usarlo en `previene/2` y agregar `nombre_problema(id, "texto")` en `chatbot.pl`.
- **Nueva regla:** agregarla en `conocimiento.pl` y, si debe responder una pregunta, una cláusula de `interpretar/1` (o de `responder_sobre_habito/2`) en `chatbot.pl`.
- La versión LLM no requiere más cambios: lee `conocimiento.pl` completo en cada consulta.
- Mantener el texto **sin tildes** en los archivos `.pl`.

## Archivos
- `conocimiento.pl`: hechos y reglas.
- `chatbot.pl`: menú y entendimiento de preguntas (normalización, entidades, intenciones).
- `chatbot_llm.py`: chatbot LLM (usa `conocimiento.pl` como contexto).
- `prolog_bridge.py`: llama a SWI-Prolog desde Python.
- `servidor.py`: servidor web y API `POST /api/chat`.
- `evaluar.py`: genera las respuestas del informe.
- `interfaz/`: frontend.
