# riesgo-api-v0

Servicio de puntuacion de siniestros para la Aseguradora Santo Tomas.

## Instalacion

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

## Desarrollo y produccion

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 2
```

## Comprobacion

```bash
curl http://localhost:8000/health
curl -X POST http://localhost:8000/score -H "Content-Type: application/json" -d "{\"poliza\":\"POL-2026-0413\",\"monto\":4200000,\"antiguedad\":3,\"siniestros_previos\":1}"
```

Las entradas invalidas responden `422`; un siniestro inexistente responde `404`; `/exportar` responde JSON.

## Mediciones

Con el servicio levantado:

```bash
python medir.py --endpoints /ping /consulta-archivo /servicio-externo /calculo-pesado --concurrencias 1 20 --peticiones 50
```

Completar `MEDICIONES.csv` con la clasificacion y decision justificadas en `HALLAZGOS.md`.
