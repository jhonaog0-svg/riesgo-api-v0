"""Predictor local pequeno y determinista para el prototipo."""


class ModeloRiesgo:
    def predict_proba(self, rasgos):
        resultado = []
        for monto, antiguedad, siniestros_previos in rasgos:
            puntaje = 0.2 + min(monto / 20_000_000, 0.5)
            puntaje += min(siniestros_previos * 0.12, 0.36)
            puntaje -= min(antiguedad * 0.005, 0.12)
            resultado.append([1.0 - max(0.0, min(1.0, puntaje)), max(0.0, min(1.0, puntaje))])
        return resultado
