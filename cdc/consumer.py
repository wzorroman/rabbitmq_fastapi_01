# file: cdc/consumer.py
from application import publicaciones_service
from application import publicaciones_service
from config import CONNECTION_DB_TARGET
import json
import pika
from db.mssql_connection import MSSQLConnector
from config import RABBITMQ_HOST, RABBITMQ_QUEUE, get_logger

logger = get_logger('cdc.consumer')

def apply_change(message: dict):
    op = message['operation']
    data = message['data']
    dest_conn = MSSQLConnector(**CONNECTION_DB_TARGET)
    with dest_conn:
        if op == 'INSERT':
            query = """
                INSERT INTO publicaciones (id_referencia, titulo, fecha, is_active)
                VALUES (?, ?, ?, ?)
            """
            dest_conn.execute_query(query, (data['id_referencia'], data['titulo'], data['fecha'], int(data['is_active'])))
        elif op == 'UPDATE':
            query = """
                UPDATE publicaciones SET titulo=?, fecha=?, is_active=?
                WHERE id=?
            """
            dest_conn.execute_query(query, (data['titulo'], data['fecha'], int(data['is_active']), data['id']))
        elif op == 'DELETE':
            query = "DELETE FROM publicaciones WHERE id=?"
            dest_conn.execute_query(query, (data['id'],))
    logger.info(f"Aplicado {op} en destino para id {data.get('id')}")


def callback(ch, method, properties, body):
    message = json.loads(body)
    try:
        apply_change(message)
        ch.basic_ack(delivery_tag=method.delivery_tag)
    except Exception as e:
        logger.error(f"Error procesando mensaje: {e}")
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)


def start_consumer():
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=RABBITMQ_HOST))
    channel = connection.channel()
    channel.queue_declare(queue=RABBITMQ_QUEUE, durable=True)
    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue=RABBITMQ_QUEUE, on_message_callback=callback)
    logger.info("Consumidor iniciado, esperando mensajes...")
    channel.start_consuming()
