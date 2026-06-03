import csv
import os
from typing import Optional

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel

from app.core.security import validar_token

router = APIRouter(
    prefix="/v1/productos",
    tags=["Productos V1"],
    dependencies=[Depends(validar_token)]
)

ARCH_PRODUCTOS = "data/productos.csv"

# ======================================================
# FUNCIONES CSV
# ======================================================

def inicializar_archivo():
    if not os.path.exists(ARCH_PRODUCTOS):
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
            row["id_producto"] = int(row["id_producto"])
            row["precio"] = float(row["precio"])
            row["stock"] = int(row["stock"])
            row["categoria"] = (
                row.get("categoria")
                or "General"
            )
            row["activo"] = (
                row["activo"] == "True"
            )
            productos.append(row)
    return productos

def guardar_productos(productos):

    with open(
        ARCH_PRODUCTOS,
        mode="w",
        newline="",
        encoding="utf-8"
    ) as f:
        campos = [
            "id_producto",
            "nombre",
            "precio",
            "stock",
            "categoria",
            "activo"
        ]
        writer = csv.DictWriter(
            f,
            fieldnames=campos
        )
        writer.writeheader()
        writer.writerows(productos)

# ======================================================
# MODELOS
# ======================================================

class ProductoCreate(BaseModel):
    nombre: str
    precio: float
    stock: int

class ProductoUpdate(BaseModel):
    id_producto: int
    nombre: Optional[str] = None
    precio: Optional[float] = None
    stock: Optional[int] = None

class ProductoDelete(BaseModel):
    id_producto: int

# ======================================================
# ENDPOINTS V1
# ======================================================

@router.get("/")
def obtener_productos():

    productos = leer_productos()
    return [
        p for p in productos
        if p["activo"]
    ]

@router.post("/", status_code=201)
def crear_producto(
    producto: ProductoCreate
):
    productos = leer_productos()
    if (
        producto.precio <= 0
        or producto.stock < 0
    ):
        raise HTTPException(
            status_code=400,
            detail="Valores inválidos"
        )
    for p in productos:
        if (
            p["activo"]
            and p["nombre"].lower()
            == producto.nombre.lower()
        ):
            raise HTTPException(
                status_code=400,
                detail="El producto ya existe"
            )
    nuevo_id = max(
        [
            p["id_producto"]
            for p in productos
        ],
        default=0
    ) + 1

    nuevo_producto = {
        "id_producto": nuevo_id,
        "nombre": producto.nombre,
        "precio": producto.precio,
        "stock": producto.stock,
        "categoria": "General",
        "activo": True
    }

    productos.append(nuevo_producto)
    guardar_productos(productos)

    return {
        "mensaje":
        "Producto agregado",
        "datos":
        nuevo_producto
    }

@router.patch("/")
def modificar_producto(
    producto: ProductoUpdate
):

    productos = leer_productos()

    for p in productos:
        if (
            p["id_producto"]
            == producto.id_producto
            and p["activo"]
        ):
            if producto.nombre:
                p["nombre"] = (
                    producto.nombre
                )
            if (
                producto.precio
                is not None
            ):
                p["precio"] = (
                    producto.precio
                )
            if (
                producto.stock
                is not None
            ):
                p["stock"] = (
                    producto.stock
                )
            guardar_productos(
                productos
            )
            return {
                "mensaje":
                "Producto modificado",
                "datos": p
            }
    raise HTTPException(
        status_code=404,
        detail="Producto no encontrado"
    )

@router.delete("/")
def eliminar_producto(
    producto: ProductoDelete
):
    productos = leer_productos()
    for p in productos:
        if (
            p["id_producto"]
            == producto.id_producto
        ):
            p["activo"] = False
            guardar_productos(
                productos
            )
            return {
                "mensaje":
                "Producto eliminado"
            }
    raise HTTPException(
        status_code=404,
        detail="Producto no encontrado"
    )