import json, os
import pika

RABBITMQ_URL = os.getenv("RABBITMQ_URL", "amqp://guest:guest@localhost:5672/")
EXCHANGE = "baches.events"
ROUTING_KEY = "bache.reportado"

def publish_reported(event: dict) -> bool:
    try:
        params = pika.URLParameters(RABBITMQ_URL)
        params.socket_timeout = 3
        connection = pika.BlockingConnection(params)
        try:
            channel = connection.channel()
            channel.exchange_declare(exchange=EXCHANGE, exchange_type="topic", durable=True)
            channel.queue_declare(queue="notificaciones.baches", durable=True)
            channel.queue_bind(queue="notificaciones.baches", exchange=EXCHANGE, routing_key=ROUTING_KEY)
            channel.basic_publish(
                exchange=EXCHANGE, routing_key=ROUTING_KEY,
                body=json.dumps(event, ensure_ascii=False).encode("utf-8"),
                properties=pika.BasicProperties(delivery_mode=2, content_type="application/json")
            )
            return True
        finally:
            connection.close()
    except Exception as exc:
        print(f"[WARN] Evento no publicado; RabbitMQ no disponible: {exc}")
        return False
