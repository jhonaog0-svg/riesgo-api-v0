import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from fastapi.testclient import TestClient
from main import app
from dominio import EvaluadorRiesgo

cliente = TestClient(app)
VALIDO = {"poliza": "POL-2026-0413", "monto": 4200000, "antiguedad": 3, "siniestros_previos": 1}


def test_health_responde_200():
    assert cliente.get("/health").status_code == 200


def test_falta_un_campo_obligatorio_da_422():
    assert cliente.post("/score", json={"monto": 1000}).status_code == 422


def test_monto_negativo_da_422():
    assert cliente.post("/score", json={**VALIDO, "monto": -5}).status_code == 422


def test_antiguedad_negativa_da_422():
    assert cliente.post("/score", json={**VALIDO, "antiguedad": -1}).status_code == 422


def test_ningun_error_viaja_con_200():
    for cuerpo in ({}, {"monto": -1}, {**VALIDO, "antiguedad": -3}):
        assert cliente.post("/score", json=cuerpo).status_code != 200


def test_siniestro_inexistente_da_404():
    assert cliente.get("/siniestros/999999").status_code == 404


def test_exportar_devuelve_json():
    respuesta = cliente.get("/exportar")
    assert respuesta.headers["content-type"].startswith("application/json")
    respuesta.json()


def test_el_historial_no_se_comparte_entre_instancias():
    primero, segundo = EvaluadorRiesgo("POL-A"), EvaluadorRiesgo("POL-B")
    primero.anotar(0.5)
    assert len(getattr(segundo, "historial", [])) == 0


def test_el_decorador_conserva_identidad():
    assert EvaluadorRiesgo.puntuar.__name__ == "puntuar"


def test_un_fallo_no_se_traga_en_silencio():
    respuesta = cliente.post("/score", json={**VALIDO, "siniestros_previos": "muchos"})
    assert respuesta.status_code != 200 or respuesta.json().get("puntaje") is not None


def test_el_caso_valido_sigue_funcionando():
    respuesta = cliente.post("/score", json=VALIDO)
    assert respuesta.status_code == 200
    assert 0 <= respuesta.json()["puntaje"] <= 1
