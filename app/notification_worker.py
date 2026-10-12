import json, os, time, pika
RABBITMQ_URL = os.getenv("RABBITMQ_URL", "amqp://guest:guest@localhost:5672/")
EXCHANGE, QUEUE, ROUTING_KEY = "baches.events", "notificaciones.baches", "bache.reportado"

def main():
    while True:
        try:
            conn = pika.BlockingConnection(pika.URLParameters(RABBITMQ_URL))
            channel = conn.channel()
            channel.exchange_declare(exchange=EXCHANGE, exchange_type="topic", durable=True)
            channel.queue_declare(queue=QUEUE, durable=True)
            channel.queue_bind(queue=QUEUE, exchange=EXCHANGE, routing_key=ROUTING_KEY)
            channel.basic_qos(prefetch_count=1)
            def on_message(ch, method, properties, body):
                try:
                    event = json.loads(body.decode("utf-8"))
                    print(f"[ALERTA SIMULADA A VECINOS] Bache #{event.get('reporte_id')} en {event.get('ubicacion')}. Severidad: {event.get('severidad')}.", flush=True)
                    ch.basic_ack(delivery_tag=method.delivery_tag)
                except Exception as exc:
                    print(f"[ERROR] Evento inválido: {exc}", flush=True)
                    ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
            channel.basic_consume(queue=QUEUE, on_message_callback=on_message)
            print("[RabbitMQ] Esperando eventos...", flush=True)
            channel.start_consuming()
        except Exception as exc:
            print(f"[RabbitMQ] {exc}; reintentando en 5 segundos", flush=True)
            time.sleep(5)

if __name__ == "__main__":
    main()
