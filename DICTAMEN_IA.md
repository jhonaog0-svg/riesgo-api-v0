# Dictamen sobre `ia_propuesta.py`

**Grupo:** por asignar · **Integrantes:** Jhon Ocampo, Paula Español, Luisa Martinez

## Defecto 1
- **Que esta mal:** El validador `redondear_monto` no retorna el valor.
- **Por que es un defecto** (M4 · Validadores): Pydantic recibe `None` y la validacion falla aunque el monto sea valido.
- **Como lo comprobamos:** `SolicitudPuntuacion(..., monto=10.129, ...).monto` produce un error de validacion.
- **Correccion:** Retornar `round(valor, 2)`.

## Defecto 2
- **Que esta mal:** `_puntuar` es asincrona pero usa `time.sleep`.
- **Por que es un defecto** (M5 · Programacion asincrona): `time.sleep` bloquea el event loop; las tareas no se ejecutan concurrentemente.
- **Como lo comprobamos:** medir un lote con varias solicitudes muestra aproximadamente la suma de las esperas, no una sola espera.
- **Correccion:** Usar `await asyncio.sleep(0.2)`.

## Defecto 3
- **Que esta mal:** El patron de correo acepta solo dominios cuya extension tenga 2 o 3 caracteres.
- **Por que es un defecto** (M4 · Validacion declarativa): rechaza direcciones validas con extensiones modernas como `.museum`.
- **Como lo comprobamos:** `SolicitudPuntuacion(correo_analista="ana@ejemplo.museum", ...)` es rechazado.
- **Correccion:** Permitir extensiones de 2 a 63 caracteres.
