# Sistema distribuido de reporte de baches — Cochabamba

Laboratorio académico con FastAPI, RabbitMQ y gRPC.

## Ejecutar
Requisitos: Docker Desktop y Docker Compose.

```bash
docker compose up --build
```

- API: http://localhost:8000
- Swagger: http://localhost:8000/docs
- RabbitMQ Management: http://localhost:15672 (guest / guest)
- gRPC: puerto 50051

## Prueba rápida
```bash
curl http://localhost:8000/health
curl -X POST http://localhost:8000/reportes -H "Content-Type: application/json" -d '{"ubicacion":"Av. América y Beijing","descripcion":"Bache en el carril derecho","severidad":"alta","reportado_por":"Vecino 001"}'
curl http://localhost:8000/reportes
curl -X POST http://localhost:8000/reparaciones/1/confirmar -H "Content-Type: application/json" -d '{"reparado_por":"Cuadrilla Municipal 3","observacion":"Bache rellenado y superficie nivelada"}'
```

La notificación es simulada y aparece en los logs del servicio `notifications`; no se envían SMS reales. SQLite se utiliza para simplificar el laboratorio.

## Endpoints
| Método | Ruta | Uso |
|---|---|---|
| GET | `/health` | Estado de la API |
| POST | `/reportes` | Registrar un bache |
| GET | `/reportes` | Listar reportes |
| GET | `/reportes/{id}` | Consultar un reporte |
| POST | `/reparaciones/{id}/confirmar` | Confirmar mediante gRPC |

Para un despliegue real se recomienda PostgreSQL, autenticación, TLS, auditoría, reintentos y patrón Outbox.
