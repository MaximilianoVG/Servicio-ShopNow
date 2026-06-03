import json
import os
import time

import requests
from dotenv import load_dotenv

from app.core.rabbitmq import get_connection


load_dotenv()

INVENTARIO_SERVICE_URL = os.getenv("INVENTARIO_SERVICE_URL", "http://inventario:8000/v2")


def procesar_pedido(ch, method, properties, body):
    try:
        pedido = json.loads(body)

        print(f"Procesando pedido desde cola: {pedido}")

        payload = {
            "id_producto": pedido["id_producto"],
            "cantidad": pedido["cantidad"]
        }

        token = obtener_token()

        headers = {
            "Authorization": f"Bearer {token}"
        }

        response = requests.delete(
            f"{INVENTARIO_SERVICE_URL.rstrip('/')}/inventario/desc",
            json=payload,
            headers=headers,
            timeout=5
        )

        if response.status_code >= 500:
            raise RuntimeError(
                f"Inventario devolvió error {response.status_code}: "
                f"{response.text.strip() or 'Error interno'}"
            )

        if response.status_code != 200:
            detalle = response.text.strip() or f"Código {response.status_code}"
            raise RuntimeError(f"No se pudo descontar inventario: {detalle}")
        
        if response.status_code == 401:

            print(
                "Token inválido"
            )
            ch.basic_ack(
                delivery_tag=method.delivery_tag
            )
            return

        print(f"Inventario descontado para pedido {pedido.get('id_producto')}")
        ch.basic_ack(delivery_tag=method.delivery_tag)

    except requests.exceptions.Timeout:
        print("Tiempo de espera agotado al contactar inventario")
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)
        time.sleep(5)

    except requests.exceptions.ConnectionError:
        print("Inventario no disponible")
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)
        time.sleep(5)

    except requests.exceptions.RequestException as exc:
        print(f"Error de red al contactar inventario: {exc}")
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)
        time.sleep(5)

    except Exception as exc:
        print(f"Error procesando pedido: {exc}")
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)
        time.sleep(5)

def obtener_token():

    response = requests.post(
        "http://inventario:8000/login",
        json={
            "username": os.getenv(
                "INVENTARIO_USER"
            ),
            "password": os.getenv(
                "INVENTARIO_PASSWORD"
            )
        },
        timeout=5
    )

    response.raise_for_status()

    return response.json()[
        "access_token"
    ]

def main():
    connection = get_connection()
    channel = connection.channel()

    channel.queue_declare(queue="cola_pedidos", durable=True)
    channel.basic_qos(prefetch_count=1)

    channel.basic_consume(
        queue="cola_pedidos",
        on_message_callback=procesar_pedido
    )

    print("Worker escuchando cola_pedidos...")
    channel.start_consuming()


if __name__ == "__main__":
    main()

