from fastapi import (
    APIRouter,
    Depends
)

from app.core.security import validar_token

import csv
import os


router = APIRouter(
    prefix="/v1",
    tags=["Inventario V1"],
    dependencies=[Depends(validar_token)]
)

ARCH_PRODUCTOS = "data/productos.csv"
ARCH_MOVIMIENTOS = "data/movimientos.csv"


# ======================================================
# FUNCIONES CSV
# ======================================================

def inicializar_archivo():

    if not os.path.exists(
        ARCH_PRODUCTOS
    ):

        with open(
            ARCH_PRODUCTOS,
            mode="w",
            newline="",
            encoding="utf-8"
        ) as f:

            writer = csv.writer(f)

            writer.writerow([
                "id_producto",
                "nombre",
                "precio",
                "stock",
                "categoria",
                "activo"
            ])


def inicializar_movimientos():

    if not os.path.exists(
        ARCH_MOVIMIENTOS
    ):

        with open(
            ARCH_MOVIMIENTOS,
            mode="w",
            newline="",
            encoding="utf-8"
        ) as f:

            writer = csv.writer(f)

            writer.writerow([
                "id_movimiento",
                "id_producto",
                "tipo",
                "cantidad",
                "stock_final",
                "fecha"
            ])


def leer_productos():

    inicializar_archivo()

    productos = []

    with open(
        ARCH_PRODUCTOS,
        mode="r",
        newline="",
        encoding="utf-8"
    ) as f:

        reader = csv.DictReader(f)

        for row in reader:

            row["id_producto"] = int(
                row["id_producto"]
            )

            row["precio"] = float(
                row["precio"]
            )

            row["stock"] = int(
                row["stock"]
            )

            row["categoria"] = (
                row.get("categoria")
                or "General"
            )

            row["activo"] = (
                row["activo"]
                == "True"
            )

            productos.append(row)

    return productos


def leer_movimientos():

    inicializar_movimientos()

    movimientos = []

    with open(
        ARCH_MOVIMIENTOS,
        mode="r",
        newline="",
        encoding="utf-8"
    ) as f:

        reader = csv.DictReader(f)

        for row in reader:

            row["id_movimiento"] = int(
                row["id_movimiento"]
            )

            row["id_producto"] = int(
                row["id_producto"]
            )

            row["cantidad"] = int(
                row["cantidad"]
            )

            row["stock_final"] = int(
                row["stock_final"]
            )

            movimientos.append(row)

    return movimientos


# ======================================================
# ENDPOINTS V1
# ======================================================

@router.get("/inventario")
def reporte_inventario_v1():

    productos = leer_productos()

    return [
        {
            "id_producto":
            p["id_producto"],

            "nombre":
            p["nombre"],

            "stock_actual":
            p["stock"]
        }

        for p in productos
        if p["activo"]
    ]


@router.get("/movimientos")
def obtener_movimientos():

    movimientos = leer_movimientos()

    return {
        "total_movimientos":
        len(movimientos),

        "movimientos":
        movimientos
    }