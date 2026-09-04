# riesgo-api-v0

Servicio de puntuacion de siniestros para la Aseguradora Santo Tomas.

## Instalacion

Desde la raiz del repositorio, abre PowerShell y ejecuta:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

En Linux o macOS:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

## Puesta en marcha

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 2
```

La API queda disponible en `http://localhost:8000`. Para detenerla, presiona `Ctrl+C`.

## Comprobacion

```bash
curl http://localhost:8000/health
curl -X POST http://localhost:8000/score -H "Content-Type: application/json" -d "{\"poliza\":\"POL-2026-0413\",\"monto\":4200000,\"antiguedad\":3,\"siniestros_previos\":1}"
```

Las entradas invalidas responden `422`; un siniestro inexistente responde `404`; `/exportar` responde JSON.

La documentacion interactiva esta en `http://localhost:8000/docs`.

## Pruebas

En otra terminal, desde la raiz del repositorio y con el entorno activado:

```bash
python -m pytest -q
```

## Mediciones

Con el servicio levantado:

```bash
python medir.py --endpoints /ping /consulta-archivo /servicio-externo /calculo-pesado --concurrencias 1 20 --peticiones 50
```

Completar `MEDICIONES.csv` con la clasificacion y decision justificadas en `HALLAZGOS.md`.
