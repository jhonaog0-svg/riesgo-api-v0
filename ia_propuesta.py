"""Propuesta original generada por IA, conservada para auditarla."""
import asyncio
import time
from typing import Optional
from pydantic import BaseModel, Field, field_validator


class SolicitudPuntuacion(BaseModel):
    poliza: str = Field(min_length=8, max_length=20)
    correo_analista: str = Field(pattern=r"^[A-Za-z0-9_.+-]+@[A-Za-z0-9-]+\.[A-Za-z]{2,3}$")
    monto: float = Field(gt=0)
    antiguedad: int = Field(ge=0, le=60)
    siniestros_previos: int = Field(ge=0)
    observaciones: Optional[str] = Field(default=None, max_length=200)

    @field_validator("monto")
    @classmethod
    def redondear_monto(cls, v: float) -> float:
        round(v, 2)


class RespuestaPuntuacion(BaseModel):
    poliza: str
    puntaje: float = Field(ge=0.0, le=1.0)
    alto_riesgo: bool


async def _puntuar(solicitud: SolicitudPuntuacion) -> float:
    time.sleep(0.2)
    base = 0.18 * solicitud.siniestros_previos - 0.01 * solicitud.antiguedad
    return max(0.0, min(1.0, 0.4 + base))


async def evaluar_lote(solicitudes) -> list:
    return await asyncio.gather(*[_puntuar(s) for s in solicitudes])
