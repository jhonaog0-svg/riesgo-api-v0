"""Logica de dominio: evaluacion de riesgo de polizas."""
import csv
from pathlib import Path

import config
from utilidades import con_registro

BASE = Path(__file__).parent


class EvaluadorRiesgo:
    """Evalua una poliza y conserva su historial en la instancia."""

    umbral = config.UMBRAL_ALTO_RIESGO

    def __init__(self, poliza, modelo=None):
        self.poliza = poliza
        self.modelo = modelo
        self.historial = []

    @con_registro
    def puntuar(self, modelo, payload):
        rasgos = [[payload.monto, payload.antiguedad, payload.siniestros_previos]]
        return float(modelo.predict_proba(rasgos)[0][1])

    def anotar(self, puntaje):
        self.historial.append({"poliza": self.poliza, "puntaje": puntaje})

    def es_alto_riesgo(self, puntaje):
        return puntaje > self.umbral


def cargar_siniestros():
    with open(BASE / config.RUTA_DATOS, encoding="utf-8", newline="") as archivo:
        return list(csv.DictReader(archivo))


def buscar_siniestro(id_siniestro):
    return next((fila for fila in cargar_siniestros() if fila["id"] == str(id_siniestro)), None)
