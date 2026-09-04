# Bitacora de uso de IA

**Grupo:** completar · **Integrantes:** completar

## Prompts

| # | Parte | Quien | Prompt |
|---|---|---|---|
| 1 | A-B | completar | Analizar el servicio y proponer un refactor bajo las restricciones del enunciado. |
| 2 | D | completar | Auditar ia_propuesta.py y demostrar sus defectos con pruebas ejecutables. |

## Aceptado

| # | Que propuso la IA | Por que lo aceptamos | Que cambiamos |
|---|---|---|---|
| 1 | Usar Pydantic para validar entradas y salidas. | Cumple el contrato 422 y hace declarativas las restricciones. | Revisamos tipos y campos. |

## Rechazado

| # | Que propuso la IA | Por que lo rechazamos | Que hicimos en su lugar |
|---|---|---|---|
| 1 | Mantener `async def` alrededor de operaciones bloqueantes. | Bloquea el event loop y la medicion no demuestra una mejora real. | Dejamos handlers sincronicos para el perfil medido. |
| 2 | Mantener `pickle` para exportar. | Es inseguro y rompe el contrato JSON. | Respondemos con modelos Pydantic serializados a JSON. |
