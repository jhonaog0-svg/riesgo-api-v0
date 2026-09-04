"""Mide los cuatro endpoints de carga y escribe MEDICIONES.csv."""
import argparse
import csv
import statistics
import time
from concurrent.futures import ThreadPoolExecutor
import httpx

ENDPOINTS = ["/ping", "/consulta-archivo", "/servicio-externo", "/calculo-pesado"]
COLUMNAS = ["endpoint", "clasificacion", "decision", "concurrencia", "peticiones", "tiempo_total_s", "p50_ms", "p95_ms"]


def percentil(muestras, q):
    xs = sorted(muestras)
    if not xs:
        return float("nan")
    posicion = (len(xs) - 1) * q / 100
    bajo = int(posicion)
    alto = min(bajo + 1, len(xs) - 1)
    return xs[bajo] + (xs[alto] - xs[bajo]) * (posicion - bajo)


def una_peticion(cliente, ruta):
    inicio = time.perf_counter()
    try:
        respuesta = cliente.get(ruta)
        return (time.perf_counter() - inicio) * 1000, respuesta.status_code < 500
    except Exception:
        return (time.perf_counter() - inicio) * 1000, False


def medir(base, ruta, concurrencia, peticiones):
    with httpx.Client(base_url=base, timeout=120) as cliente:
        for _ in range(3):
            una_peticion(cliente, ruta)
        inicio = time.perf_counter()
        with ThreadPoolExecutor(max_workers=concurrencia) as executor:
            resultados = list(executor.map(lambda _: una_peticion(cliente, ruta), range(peticiones)))
    latencias = [ms for ms, ok in resultados if ok]
    if len(latencias) != peticiones:
        raise RuntimeError(f"Fallaron {peticiones - len(latencias)} peticiones a {ruta}")
    return {"endpoint": ruta, "clasificacion": "", "decision": "", "concurrencia": concurrencia,
            "peticiones": peticiones, "tiempo_total_s": round(time.perf_counter() - inicio, 3),
            "p50_ms": round(statistics.median(latencias), 1), "p95_ms": round(percentil(latencias, 95), 1)}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--base", default="http://localhost:8000")
    parser.add_argument("--endpoints", nargs="+", default=ENDPOINTS)
    parser.add_argument("--concurrencias", nargs="+", type=int, default=[1, 20])
    parser.add_argument("--peticiones", type=int, default=50)
    parser.add_argument("--salida", default="MEDICIONES.csv")
    args = parser.parse_args()
    filas = [medir(args.base, endpoint, concurrencia, args.peticiones)
             for endpoint in args.endpoints for concurrencia in args.concurrencias]
    with open(args.salida, "w", newline="", encoding="utf-8") as archivo:
        escritor = csv.DictWriter(archivo, fieldnames=COLUMNAS)
        escritor.writeheader()
        escritor.writerows(filas)


if __name__ == "__main__":
    main()
