import json
import pika
from config import RABBITMQ_HOST, RABBITMQ_QUEUE, get_logger

logger = get_logger('cdc.producer')

def publish_change(operation: str, data: dict):
    try:
        connection = pika.BlockingConnection(pika.ConnectionParameters(host=RABBITMQ_HOST))
        channel = connection.channel()
        channel.queue_declare(queue=RABBITMQ_QUEUE, durable=True)

        message = {
            "operation": operation,   # 'INSERT', 'UPDATE', 'DELETE'
            "table": "publicaciones",
            "data": data
        }
        channel.basic_publish(
            exchange='',
            routing_key=RABBITMQ_QUEUE,
            body=json.dumps(message),
            properties=pika.BasicProperties(delivery_mode=2)  # persistente
        )
        connection.close()
        logger.info(f"Evento {operation} publicado para id {data.get('id')}")
    except Exception as e:
        logger.error(f"Error publicando en RabbitMQ: {e}")
