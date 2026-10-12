import os
from contextlib import asynccontextmanager
from typing import Literal
import grpc
from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field
from app import database
from app.events import publish_reported
import reparaciones_pb2
import reparaciones_pb2_grpc

GRPC_TARGET = os.getenv("GRPC_TARGET", "localhost:50051")

@asynccontextmanager
async def lifespan(app: FastAPI):
    database.init_db()
    yield

app = FastAPI(title="Sistema de Reporte de Baches — Cochabamba",
              description="API REST con RabbitMQ y confirmación gRPC.",
              version="1.0.0", lifespan=lifespan)

class ReporteCreate(BaseModel):
    ubicacion: str = Field(min_length=3, max_length=200)
    descripcion: str = Field(min_length=5, max_length=1000)
    severidad: Literal["baja", "media", "alta"] = "media"
    reportado_por: str = Field(min_length=2, max_length=100)

class ConfirmacionCreate(BaseModel):
    reparado_por: str = Field(min_length=2, max_length=100)
    observacion: str = Field(min_length=3, max_length=500)

@app.get("/health")
def health():
    return {"estado": "ok", "servicio": "reportes"}

@app.post("/reportes", status_code=status.HTTP_201_CREATED)
def crear_reporte(payload: ReporteCreate):
    reporte = database.create_report(payload.model_dump())
    evento = {"tipo": "bache.reportado", "reporte_id": reporte["id"],
              "ubicacion": reporte["ubicacion"], "descripcion": reporte["descripcion"],
              "severidad": reporte["severidad"]}
    publicado = publish_reported(evento)
    return {"reporte": reporte, "evento_publicado": publicado,
            "nota": "El reporte se guardó. Si RabbitMQ no estaba disponible, el evento no se publicó."}

@app.get("/reportes")
def listar_reportes():
    return database.list_reports()

@app.get("/reportes/{reporte_id}")
def consultar_reporte(reporte_id: int):
    reporte = database.get_report(reporte_id)
    if not reporte:
        raise HTTPException(status_code=404, detail="Reporte no encontrado")
    return reporte

@app.post("/reparaciones/{reporte_id}/confirmar")
def confirmar_reparacion(reporte_id: int, payload: ConfirmacionCreate):
    if not database.get_report(reporte_id):
        raise HTTPException(status_code=404, detail="Reporte no encontrado")
    try:
        with grpc.insecure_channel(GRPC_TARGET) as channel:
            stub = reparaciones_pb2_grpc.ReparacionesServiceStub(channel)
            respuesta = stub.ConfirmarReparacion(
                reparaciones_pb2.ConfirmarReparacionRequest(
                    reporte_id=reporte_id, reparado_por=payload.reparado_por,
                    observacion=payload.observacion), timeout=5)
    except grpc.RpcError as exc:
        raise HTTPException(status_code=503, detail=f"Servicio gRPC no disponible: {exc.code().name}") from exc
    if not respuesta.confirmado:
        raise HTTPException(status_code=409, detail=respuesta.mensaje)
    actualizado = database.mark_repaired(reporte_id, payload.reparado_por, payload.observacion)
    return {"confirmacion_grpc": {"confirmado": respuesta.confirmado,
            "reporte_id": respuesta.reporte_id, "estado": respuesta.estado,
            "mensaje": respuesta.mensaje}, "reporte_actualizado": actualizado}
