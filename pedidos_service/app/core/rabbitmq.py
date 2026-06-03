import json
import os
import time

import pika
from dotenv import load_dotenv

load_dotenv()

def get_connection():
    rabbitmq_url = os.getenv(
        "RABBITMQ_URL"
    )
    for i in range(10):
        try:
            print(
                f"Intento {i + 1} de conexión a RabbitMQ..."
            )
            params = pika.URLParameters(
                rabbitmq_url
            )
            connection = pika.BlockingConnection(
                params
            )
            print(
                "Conectado a CloudAMQP"
            )
            return connection
        except Exception as e:
            print(
                f"RabbitMQ no disponible: {e}"
            )
            time.sleep(3)
    raise Exception(
        "No se pudo conectar a RabbitMQ después de varios intentos"
    )

def publicar_pedido_cola(
    pedido: dict
):
    connection = get_connection()
    try:
        channel = connection.channel()
        channel.queue_declare(
            queue="cola_pedidos",
            durable=True
        )
        channel.basic_publish(
            exchange="",
            routing_key="cola_pedidos",
            body=json.dumps(pedido),
            properties=pika.BasicProperties(
                delivery_mode=2
            )
        )
        print(
            f"Pedido publicado en cola_pedidos: {pedido}"
        )
    finally:
        connection.close()