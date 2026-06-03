from fastapi import (
    APIRouter,
    HTTPException,
    Depends
)

from pydantic import (
    BaseModel,
    Field
)

from typing import Optional
import requests
import os
from dotenv import load_dotenv

from app.core.security import validar_token
from app.core.db import get_connection
from app.core.rabbitmq import publicar_pedido_cola

load_dotenv()

router = APIRouter(
    prefix="/v2/pedidos",
    tags=["Pedidos V2"],
    dependencies=[Depends(validar_token)]
)

# ======================================================
# URLS DE MICROSERVICIOS
# ======================================================

CLIENTES_URL = os.getenv(
    "CLIENTES_SERVICE_URL"
)

PRODUCTOS_URL = os.getenv(
    "PRODUCTOS_SERVICE_URL"
)

# ======================================================
# MODELO
# ======================================================

class PedidoCreateV2(BaseModel):

    id_cliente: int = Field(
        ...,
        example=1
    )

    id_producto: int = Field(
        ...,
        example=1
    )

    cantidad: int = Field(
        ...,
        gt=0,
        example=2
    )

    descuento: Optional[float] = Field(
        default=0,
        example=10
    )


def construir_url_servicio(
    base_url: str,
    id_recurso: int,
    marcador: str
) -> str:

    if not base_url:
        raise HTTPException(
            status_code=503,
            detail="Servicio de pedidos no disponible"
        )

    url = base_url.rstrip("/")

    if marcador in url:
        url = url.replace(marcador, str(id_recurso))
    else:
        url = f"{url}/{id_recurso}"

    return url


def extraer_detalle_respuesta(response: requests.Response) -> str:

    try:
        data = response.json()

        if isinstance(data, dict):
            detail = data.get("detail")

            if detail:
                return str(detail)

    except ValueError:
        pass

    texto = response.text.strip()

    if texto:
        return texto

    return f"Respuesta con código {response.status_code}"


def consultar_servicio(
    nombre_servicio: str,
    url: str,
    id_recurso: int
):

    try:
        response = requests.get(
            url,
            timeout=5
        )

    except requests.exceptions.Timeout:

        raise HTTPException(
            status_code=503,
            detail=(
                f"Servicio de {nombre_servicio} no disponible"
            )
        )

    except requests.exceptions.ConnectionError:

        raise HTTPException(
            status_code=503,
            detail=(
                f"Servicio de {nombre_servicio} no disponible"
            )
        )

    except requests.exceptions.RequestException:

        raise HTTPException(
            status_code=503,
            detail=(
                f"Servicio de {nombre_servicio} no disponible"
            )
        )

    if response.status_code == 404:

        raise HTTPException(
            status_code=404,
            detail=(
                f"{nombre_servicio.capitalize()} con ID "
                f"{id_recurso} no encontrado"
            )
        )

    if response.status_code == 503:

        raise HTTPException(
            status_code=503,
            detail=(
                f"Servicio de {nombre_servicio} no disponible"
            )
        )

    if response.status_code == 403:

        raise HTTPException(
            status_code=503,
            detail=(
                f"El servicio de {nombre_servicio} rechazó la "
                f"solicitud: {extraer_detalle_respuesta(response)}"
            )
        )

    if response.status_code >= 500:

        raise HTTPException(
            status_code=502,
            detail=(
                f"El servicio de {nombre_servicio} falló "
                f"internamente: {extraer_detalle_respuesta(response)}"
            )
        )

    if response.status_code != 200:

        raise HTTPException(
            status_code=502,
            detail=(
                f"Respuesta inesperada del servicio de "
                f"{nombre_servicio}: {response.status_code} - "
                f"{extraer_detalle_respuesta(response)}"
            )
        )

    try:
        return response.json()

    except ValueError:

        raise HTTPException(
            status_code=502,
            detail=(
                f"El servicio de {nombre_servicio} devolvió una "
                "respuesta inválida"
            )
        )


# ======================================================
# GET PEDIDOS
# ======================================================

@router.get("/")
def obtener_pedidos():

    conn = get_connection()
    cur = conn.cursor()

    try:

        cur.execute(
            """
            SELECT * 
            FROM mvg_pedidos()
            """
        )

        rows = cur.fetchall()

        pedidos = []

        for row in rows:

            pedidos.append({

                "id_pedido": row[0], 
                "id_cliente": row[1], 
                "id_producto": row[2], 
                "cantidad": row[3], 
                "estado": row[4], 
                "descuento_pct": float(row[5]), 
                "total": float(row[6]), 
                "fecha_pedido": row[7]

            })

        return {

            "total_pedidos":
            len(pedidos),

            "pedidos":
            pedidos

        }

    except Exception:

        raise HTTPException(
            status_code=500,
            detail="Error interno al consultar los pedidos"
        )

    finally:

        cur.close()
        conn.close()


# ======================================================
# POST PEDIDO
# ======================================================

@router.post("/", status_code=201)
def crear_pedido(
    pedido: PedidoCreateV2
):

    conn = get_connection()
    cur = conn.cursor()

    try:

        # =====================================
        # VALIDAR CLIENTE
        # =====================================

        cliente_url = construir_url_servicio(
            CLIENTES_URL,
            pedido.id_cliente,
            "{id_cliente}"
        )

        cliente = consultar_servicio(
            "clientes",
            cliente_url,
            pedido.id_cliente
        )

        # =====================================
        # VALIDAR PRODUCTO
        # =====================================

        producto_url = construir_url_servicio(
            PRODUCTOS_URL,
            pedido.id_producto,
            "{id_producto}"
        )

        producto = consultar_servicio(
            "productos",
            producto_url,
            pedido.id_producto
        )

        # =====================================
        # OBTENER COSTO AUTOMÁTICO
        # =====================================

        try:
            precio_unitario = producto[
                "precio"
            ]
        except KeyError:
            raise HTTPException(
                status_code=502,
                detail=(
                    "El servicio de productos devolvió una "
                    "respuesta incompleta: falta el campo 'precio'"
                )
            )

        # =====================================
        # CREAR PEDIDO
        # =====================================

        cur.execute(
            """
            CALL mvg_pedidos_agregar(
                %s,
                %s,
                %s,
                %s
            )
            """,
            (
                pedido.id_cliente,
                pedido.id_producto,
                pedido.cantidad,
                pedido.descuento,
            )
        )

        conn.commit()

        try:
            publicar_pedido_cola({
                "id_cliente": pedido.id_cliente,
                "id_producto": pedido.id_producto,
                "cantidad": pedido.cantidad,
                "descuento": pedido.descuento,
            })

        except Exception as exc:
            print(f"No se pudo publicar el pedido en RabbitMQ: {exc}")

        return {

            "mensaje":
            "Pedido creado correctamente",

            "pedido": {

                "id_cliente":
                pedido.id_cliente,
                "id_producto":
                pedido.id_producto,
                "cantidad":
                pedido.cantidad,
                "precio_unitario":
                precio_unitario,
                "descuento":
                pedido.descuento
            }

        }

    except HTTPException:

        raise

    except Exception:

        conn.rollback()

        raise HTTPException(
            status_code=500,
            detail="Error interno al crear el pedido"
        )

    finally:

        cur.close()
        conn.close()