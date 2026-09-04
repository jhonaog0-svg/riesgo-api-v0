# Hallazgos - Parte A

**Grupo:** completar · **Integrantes:** completar

> Sustituye `SALIDA_PENDIENTE` por la salida literal obtenida al ejecutar cada comando sobre la semilla. No inventes resultados ni dejes el SHA final: usa `v0-semilla` o el SHA real indicado por el curso.

| ID | Sintoma observable | Causa | Modulo · Seccion | SHA donde se observa | Comando de evidencia | Salida obtenida | Correccion aplicada |
|---|---|---|---|---|---|---|---|
| H1 | Un monto negativo puede terminar en error 500 por un `assert`. | `assert` no es validacion HTTP de entrada. | M2 · El protocolo HTTP y la autenticacion | v0-semilla | `curl -s -o /dev/null -w "%{http_code}" -X POST localhost:8000/score -H "Content-Type: application/json" -d "{\"poliza\":\"POL-2026-0413\",\"monto\":-5,\"antiguedad\":3,\"siniestros_previos\":1}"` | SALIDA_PENDIENTE | Modelo Pydantic con `Field(gt=0)`, respuesta 422. |
| H2 | Una entrada sin campos obligatorios responde error dentro de JSON con 200. | El handler recibe `dict` y devuelve errores manualmente. | M4 · Modelos de validacion | v0-semilla | `curl -s -o /dev/null -w "%{http_code}" -X POST localhost:8000/score -H "Content-Type: application/json" -d "{}"` | SALIDA_PENDIENTE | Entrada declarada como `BaseModel`. |
| H3 | `/exportar` devuelve `application/octet-stream`. | Se usa `pickle` hacia el cliente. | M2 · Serializacion | v0-semilla | `curl -sI localhost:8000/exportar` | SALIDA_PENDIENTE | Respuesta JSON con modelo Pydantic. |
| H4 | Un siniestro inexistente responde 200 con un error en el cuerpo. | No se lanza `HTTPException(404)`. | M2 · El protocolo HTTP y la autenticacion | v0-semilla | `curl -s -o /dev/null -w "%{http_code}" localhost:8000/siniestros/999999` | SALIDA_PENDIENTE | `HTTPException` con estado 404. |
| H5 | El historial se comparte entre evaluadores. | `historial` es una lista mutable de clase. | M3 · Clases y objetos | v0-semilla | `pytest -q tests/test_contrato.py -k historial` | SALIDA_PENDIENTE | Historial por instancia y estado explicito de aplicacion. |
| H6 | Un fallo del dominio devuelve `None` y puede producir 200. | El decorador captura excepciones y oculta el fallo. | M1 · Funciones decoradoras | v0-semilla | `pytest -q tests/test_contrato.py -k fallo` | SALIDA_PENDIENTE | `wraps` conserva metadata y la excepcion se propaga. |
| H7 | El modelo se carga en cada solicitud. | `pickle.load` esta dentro de `/score`. | M5 · Arquitectura de una API | v0-semilla | `rg "pickle.load" main.py` | SALIDA_PENDIENTE | Predictor cargado una vez al iniciar el modulo. |
| H8 | Los handlers async bloquean el event loop. | `time.sleep` y el calculo CPU viven en `async def`. | M5 · Programacion asincrona | v0-semilla | `rg -n "async def|time.sleep|range\(3_000_000\)" main.py` | SALIDA_PENDIENTE | Handlers bloqueantes declarados como `def`. |

# Parte C - Interpretacion de las mediciones

## `/ping`

Es trivial: devuelve una constante y la diferencia entre concurrencia 1 y 20 debe ser pequena. Se conserva `async def` porque no bloquea y expresa correctamente que el handler no necesita espera externa.

## `/consulta-archivo`

Es I/O-bound, pero la lectura usada es sincrona y el archivo es pequeno. La medicion debe mostrar poca diferencia entre concurrencias; por eso se deja `def`, evitando presentar como asincronia una operacion que no ofrece beneficio medible en este contexto.

## `/servicio-externo`

Es I/O-bound por la espera de red simulada, pero el servicio entregado usa una llamada bloqueante. Con concurrencia 20 el servidor puede atender solicitudes en hilos y el tiempo total debe acercarse a varias esperas solapadas. La decision se conserva como `def` porque es coherente con la implementacion medida.

## `/calculo-pesado`

Es CPU-bound. La concurrencia 20 no debe reducir proporcionalmente el tiempo y puede aumentar p95 por contencion; por eso se declara `def`. Si se necesitara liberar el event loop, la alternativa seria `async def + executor`, pero debe medirse y justificarse, no asumirse.
