from concurrent import futures
import time, grpc
import reparaciones_pb2
import reparaciones_pb2_grpc

class ReparacionesService(reparaciones_pb2_grpc.ReparacionesServiceServicer):
    def ConfirmarReparacion(self, request, context):
        if request.reporte_id <= 0 or not request.reparado_por.strip():
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details("ID positivo y responsable de reparación son obligatorios.")
            return reparaciones_pb2.ConfirmarReparacionResponse(
                confirmado=False, reporte_id=request.reporte_id,
                estado="rechazado", mensaje="Datos de confirmación inválidos")
        print(f"[gRPC] Reparación confirmada para reporte #{request.reporte_id} por {request.reparado_por}", flush=True)
        return reparaciones_pb2.ConfirmarReparacionResponse(
            confirmado=True, reporte_id=request.reporte_id, estado="reparado",
            mensaje="La reparación fue confirmada por el servicio gRPC.")

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    reparaciones_pb2_grpc.add_ReparacionesServiceServicer_to_server(ReparacionesService(), server)
    server.add_insecure_port("[::]:50051")
    server.start()
    print("[gRPC] Servicio de reparaciones escuchando en puerto 50051", flush=True)
    try:
        while True: time.sleep(86400)
    except KeyboardInterrupt:
        server.stop(grace=3)

if __name__ == "__main__":
    serve()
