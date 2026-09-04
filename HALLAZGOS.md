# Hallazgos - Parte A

**Grupo:** por asignar · **Integrantes:** Jhon Ocampo, Paula Español, Luisa Martinez

> Sustituye `SALIDA_PENDIENTE` por la salida literal obtenida al ejecutar cada comando sobre la semilla. No inventes resultados ni dejes el SHA final: usa `v0-semilla` o el SHA real indicado por el curso.

| ID | Sintoma observable | Causa | Modulo · Seccion | SHA donde se observa | Comando de evidencia | Salida obtenida | Correccion aplicada |
|---|---|---|---|---|---|---|---|
| H1 | Un monto negativo puede terminar en error 500 por un `assert`. | `assert` no es validacion HTTP de entrada. | M2 · El protocolo HTTP y la autenticacion | v0-semilla | `curl -s -o /dev/null -w "%{http_code}" -X POST localhost:8000/score -H "Content-Type: application/json" -d "{\"poliza\":\"POL-2026-0413\",\"monto\":-5,\"antiguedad\":3,\"siniestros_previos\":1}"` | 500 | Modelo Pydantic con `Field(gt=0)`, respuesta 422. |
| H2 | Una entrada sin campos obligatorios responde error dentro de JSON con 200. | El handler recibe `dict` y devuelve errores manualmente. | M4 · Modelos de validacion | v0-semilla | `curl -s -o /dev/null -w "%{http_code}" -X POST localhost:8000/score -H "Content-Type: application/json" -d "{}"` | 200 | Entrada declarada como `BaseModel`. |
| H3 | `/exportar` devuelve `application/octet-stream`. | Se usa `pickle` hacia el cliente. | M2 · Serializacion | v0-semilla | `curl -sI localhost:8000/exportar` | 200; application/octet-stream | Respuesta JSON con modelo Pydantic. |
| H4 | Un siniestro inexistente responde 200 con un error en el cuerpo. | No se lanza `HTTPException(404)`. | M2 · El protocolo HTTP y la autenticacion | v0-semilla | `curl -s -o /dev/null -w "%{http_code}" localhost:8000/siniestros/999999` | 200 | `HTTPException` con estado 404. |
| H5 | El historial se comparte entre evaluadores. | `historial` es una lista mutable de clase. | M3 · Clases y objetos | v0-semilla | `pytest -q tests/test_contrato.py -k historial` | 1 failed, 10 deselected | Historial por instancia y estado explicito de aplicacion. |
| H6 | Un fallo del dominio devuelve `None` y puede producir 200. | El decorador captura excepciones y oculta el fallo. | M1 · Funciones decoradoras | v0-semilla | `pytest -q tests/test_contrato.py -k fallo` | 200; {"poliza":"POL-2026-0413","puntaje":null,"alto_riesgo":false} | `wraps` conserva metadata y la excepcion se propaga. |
| H7 | El modelo se carga en cada solicitud. | `pickle.load` esta dentro de `/score`. | M5 · Arquitectura de una API | v0-semilla | `rg "pickle.load" main.py` | `main.py:29:        modelo = pickle.load(fh)` | Predictor cargado una vez al iniciar el modulo. |
| H8 | Los handlers async bloquean el event loop. | `time.sleep` y el calculo CPU viven en `async def`. | M5 · Programacion asincrona | v0-semilla | `rg -n "async def|time.sleep|range\(3_000_000\)" main.py` | `19:async def score(payload: dict)`; `29:        modelo = pickle.load(fh)`; `43:async def historial()`; `48:async def siniestro(id_siniestro: int)`; `56:async def exportar()`; `64:async def ping()`; `69:async def consulta_archivo()`; `75:async def servicio_externo()`; `76:    time.sleep(0.3)`; `81:async def calculo_pesado()`; `83:    for i in range(3_000_000):` | Handlers bloqueantes declarados como `def`. |

# Parte C - Interpretacion de las mediciones

## `/ping`

Es trivial: devuelve una constante. Con concurrencia 1 tomo 0.044 s, p50 de 0.7 ms y p95 de 1.2 ms; con 20 el total sube a 2.055 s y el p95 llega a 2043.8 ms. La ruta sigue siendo trivial y `async def` no bloquea, pero la cola de solicitudes y los dos workers explican que aumentar la concurrencia no mejore automáticamente la latencia.

## `/consulta-archivo`

Es I/O-bound, pero la lectura sincrona del archivo es muy pequena. Con concurrencia 1 tarda 0.065 s, con p50 de 1.2 ms y p95 de 1.4 ms; con 20 tarda 2.060 s y el p95 sube a 2054.2 ms. El resultado no justifica convertir esta lectura pequena en una operacion asincrona, por eso se deja `def`.

## `/servicio-externo`

Es I/O-bound por la espera simulada de 0.3 s, pero la implementacion usa una llamada bloqueante. Con concurrencia 1 tarda 15.176 s, p50 de 303.6 ms y p95 de 304.1 ms; con 20 baja a 2.943 s por el solapamiento en los workers, aunque el p95 sube a 2356.9 ms. Se conserva `def` porque es la decision coherente con la implementacion sincrona medida.

## `/calculo-pesado`

Es CPU-bound. Con concurrencia 1 tarda 15.710 s, p50 de 301.6 ms y p95 de 361.1 ms; con 20 solo baja a 12.830 s, mientras el p50 sube a 543.3 ms y el p95 a 12654.7 ms. La mejora del total no compensa la cola y la variabilidad, así que se declara `def`; un executor sería una alternativa para liberar el event loop, pero debe medirse antes de adoptarlo.
