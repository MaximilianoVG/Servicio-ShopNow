from fastapi import (
    APIRouter,
    HTTPException,
    Depends
)

from pydantic import BaseModel
from typing import List

from app.core.security import validar_token
from datetime import datetime

import csv
import os
import json


router = APIRouter(
    prefix="/v1/pedidos",
    tags=["Pedidos V1"],
    dependencies=[Depends(validar_token)]
)

ARCH_PEDIDOS = "data/pedidos.csv"


# ======================================================
# FUNCIONES CSV
# ======================================================

def inicializar_archivo():

    if not os.path.exists(
        ARCH_PEDIDOS
    ):

        with open(
            ARCH_PEDIDOS,
            mode="w",
            newline="",
            encoding="utf-8"
        ) as f:

            writer = csv.writer(f)

            writer.writerow([
                "id_pedido",
                "id_cliente",
                "productos",
                "total",
                "fecha_compra",
                "activo"
            ])


def leer_pedidos():

    inicializar_archivo()

    pedidos = []

    with open(
        ARCH_PEDIDOS,
        mode="r",
        newline="",
        encoding="utf-8"
    ) as f:

        reader = csv.DictReader(f)

        for row in reader:

            row["id_pedido"] = int(
                row["id_pedido"]
            )

            row["id_cliente"] = int(
                row["id_cliente"]
            )

            row["total"] = float(
                row["total"]
            )

            row["productos"] = json.loads(
                row["productos"]
            )

            row["activo"] = (
                row["activo"]
                == "True"
            )

            pedidos.append(row)

    return pedidos


def guardar_pedidos(
    pedidos
):

    with open(
        ARCH_PEDIDOS,
        mode="w",
        newline="",
        encoding="utf-8"
    ) as f:

        campos = [
            "id_pedido",
            "id_cliente",
            "productos",
            "total",
            "fecha_compra",
            "activo"
        ]

        writer = csv.DictWriter(
            f,
            fieldnames=campos
        )

        writer.writeheader()

        for p in pedidos:

            fila = p.copy()

            fila["productos"] = (
                json.dumps(
                    fila["productos"]
                )
            )

            writer.writerow(
                fila
            )


# ======================================================
# MODELOS
# ======================================================

class ProductoPedido(
    BaseModel
):
    id_producto: int
    cantidad: int
    precio_unitario: float


class PedidoCreate(
    BaseModel
):
    id_cliente: int
    productos: List[
        ProductoPedido
    ]
    total: float


# ======================================================
# ENDPOINTS V1
# ======================================================

@router.get("/")
def obtener_pedidos():

    return leer_pedidos()


@router.post(
    "/",
    status_code=201
)
def crear_pedido(
    data:
    PedidoCreate
):

    pedidos = leer_pedidos()

    if data.total <= 0:

        raise HTTPException(
            status_code=400,
            detail="Total inválido"
        )

    nuevo_id = max(
        [
            p["id_pedido"]
            for p in pedidos
        ],
        default=0
    ) + 1

    nuevo_pedido = {

        "id_pedido":
        nuevo_id,

        "id_cliente":
        data.id_cliente,

        "productos":
        [
            p.model_dump()
            for p in data.productos
        ],

        "total":
        data.total,

        "fecha_compra":
        datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        ),

        "activo":
        True
    }

    pedidos.append(
        nuevo_pedido
    )

    guardar_pedidos(
        pedidos
    )

    return {
        "mensaje":
        "Pedido registrado",

        "datos":
        nuevo_pedido
    }