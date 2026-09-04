"""API de puntuacion de siniestros."""
import time
from pathlib import Path

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, ConfigDict, Field, field_validator

import config
from dominio import EvaluadorRiesgo, buscar_siniestro, cargar_siniestros
from modelo import ModeloRiesgo

BASE = Path(__file__).parent
modelo = ModeloRiesgo()
app = FastAPI(title="Riesgo API", version="1.0.0")
app.state.evaluaciones = []


class SolicitudPuntuacion(BaseModel):
    model_config = ConfigDict(extra="forbid")
    poliza: str = Field(min_length=8, max_length=20)
    monto: float = Field(gt=0)
    antiguedad: int = Field(ge=0, le=60)
    siniestros_previos: int = Field(ge=0)

    @field_validator("monto")
    @classmethod
    def normalizar_monto(cls, valor):
        return round(valor, 2)


class RespuestaPuntuacion(BaseModel):
    poliza: str
    puntaje: float = Field(ge=0, le=1)
    alto_riesgo: bool


class HistorialResponse(BaseModel):
    evaluaciones: list["Evaluacion"]


class Evaluacion(BaseModel):
    poliza: str
    puntaje: float = Field(ge=0, le=1)


class Siniestro(BaseModel):
    id: int
    poliza: str
    monto: float
    antiguedad: int
    siniestros_previos: int
    pago_alto: int


class HistorialSiniestros(BaseModel):
    registros: list[Siniestro]


class ConteoResponse(BaseModel):
    lineas: int


class TarifaResponse(BaseModel):
    tarifa_referencia: float


class CalculoResponse(BaseModel):
    total: float


class EstadoResponse(BaseModel):
    estado: str


class PingResponse(BaseModel):
    pong: bool


@app.post("/score", response_model=RespuestaPuntuacion)
def score(payload: SolicitudPuntuacion):
    evaluador = EvaluadorRiesgo(payload.poliza, modelo)
    puntaje = evaluador.puntuar(modelo, payload)
    evaluador.anotar(puntaje)
    app.state.evaluaciones.append(Evaluacion(poliza=payload.poliza, puntaje=puntaje))
    return RespuestaPuntuacion(
        poliza=payload.poliza,
        puntaje=puntaje,
        alto_riesgo=evaluador.es_alto_riesgo(puntaje),
    )


@app.get("/historial", response_model=HistorialResponse)
def historial():
    return HistorialResponse(evaluaciones=app.state.evaluaciones)


@app.get("/siniestros/{id_siniestro}", response_model=Siniestro)
def siniestro(id_siniestro: int):
    fila = buscar_siniestro(id_siniestro)
    if fila is None:
        raise HTTPException(status_code=404, detail="Siniestro no encontrado")
    return Siniestro(**fila)


@app.get("/exportar", response_model=HistorialSiniestros)
def exportar():
    return HistorialSiniestros(registros=cargar_siniestros())


@app.get("/health", response_model=EstadoResponse)
def health():
    return EstadoResponse(estado="ok")


@app.get("/ping", response_model=PingResponse)
async def ping():
    return PingResponse(pong=True)


@app.get("/consulta-archivo", response_model=ConteoResponse)
def consulta_archivo():
    contenido = (BASE / config.RUTA_DATOS).read_text(encoding="utf-8")
    return ConteoResponse(lineas=len(contenido.splitlines()))


@app.get("/servicio-externo", response_model=TarifaResponse)
def servicio_externo():
    time.sleep(0.3)
    return TarifaResponse(tarifa_referencia=1.18)


@app.get("/calculo-pesado", response_model=CalculoResponse)
def calculo_pesado():
    total = sum((i % 7) ** 0.5 for i in range(3_000_000))
    return CalculoResponse(total=round(total, 2))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, workers=2)
