"""Configuracion del servicio mediante variables de entorno."""
import os

UMBRAL_ALTO_RIESGO = float(os.getenv("UMBRAL_ALTO_RIESGO", "0.7"))
RUTA_DATOS = os.getenv("RUTA_DATOS", "datos/siniestros.csv")
