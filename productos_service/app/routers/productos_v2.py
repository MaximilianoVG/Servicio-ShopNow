from operator import le
from typing import Optional
from fastapi import (
    APIRouter,
    HTTPException,
    Depends
)
from pydantic import (
    BaseModel,
    Field
)
import psycopg2
from app.core.db import (
    get_connection
)
from app.core.security import (
    validar_token
)
router = APIRouter(
    prefix="/v2/productos",
    tags=["Productos V2"]
)

# ======================================================
# MODELOS
# ======================================================

class ProductoCreateV2(BaseModel):

    descripcion: str = Field(
        ...,
        example="Laptop HP"
    )
    precio: float = Field(
        ...,
        example=15000
    )

class ProductoUpdateV2(BaseModel):
    id_producto: int
    descripcion: Optional[str] = None
    precio: Optional[float] = None
    activo: Optional[bool] = None

class ProductoDeleteV2(BaseModel):
    id_producto: int


def servicio_no_disponible():
    raise HTTPException(
        status_code=503,
        detail="Servicio de productos no disponible"
    )


# ======================================================
# ENDPOINTS V2
# ======================================================

@router.get("/",
    dependencies=[Depends(validar_token)])
def obtener_productos():

    conn = None
    cur = None

    try:
        conn = get_connection()
        cur = conn.cursor()

        cur.execute(
            "SELECT * FROM mvg_productos()"
        )
        rows = cur.fetchall()
        productos = []
        for row in rows:

            productos.append({
                "id_producto":
                row[0],
                "descripcion":
                row[1],
                "precio":
                float(row[2]),
                "activo":
                row[3]
            })
        return {
            "total_productos":
            len(productos),
            "productos":
            productos
        }
    except psycopg2.Error:
        servicio_no_disponible()
    finally:
        if cur is not None:
            cur.close()
        if conn is not None:
            conn.close()

@router.post("/", 
    status_code=201,
    dependencies=[Depends(validar_token)])
def crear_producto(
    producto: ProductoCreateV2
):
    conn = None
    cur = None

    try:
        conn = get_connection()
        cur = conn.cursor()

        cur.execute(
            """
            CALL mvg_productos_insertar (
                %s,%s
            )
            """,
            (
                producto.descripcion,
                producto.precio
            )
        )
        conn.commit()
        return {
            "mensaje":
            "Producto creado correctamente"
        }
    except psycopg2.Error:
        if conn is not None:
            conn.rollback()
        servicio_no_disponible()
    except Exception as e:

        if conn is not None:
            conn.rollback()
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

    finally:
        if cur is not None:
            cur.close()
        if conn is not None:
            conn.close()

@router.patch("/",
    dependencies=[Depends(validar_token)])
def modificar_producto(
    producto: ProductoUpdateV2
):
    conn = None
    cur = None

    try:
        conn = get_connection()
        cur = conn.cursor()

        cur.execute(
            """
            CALL mvg_productos_modificar(
                %s,%s,%s,%s
            )
            """,
            (
                producto.id_producto,
                producto.descripcion,
                producto.precio,
                producto.activo,
            )
        )
        conn.commit()
        return {
            "mensaje":
            "Producto actualizado"
        }
    except psycopg2.Error:
        if conn is not None:
            conn.rollback()
        servicio_no_disponible()
    except Exception as e:

        if conn is not None:
            conn.rollback()
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )
    finally:
        if cur is not None:
            cur.close()
        if conn is not None:
            conn.close()

@router.delete("/",
    dependencies=[Depends(validar_token)])
def eliminar_producto(
    producto: ProductoDeleteV2
):
    conn = None
    cur = None

    try:
        conn = get_connection()
        cur = conn.cursor()

        cur.execute(
            """
            CALL mvg_productos_eliminar(%s)
            """,
            (
                producto.id_producto,
            )
        )
        conn.commit()

        return {
            "mensaje":
            "Producto eliminado"
        }
    except psycopg2.Error:
        if conn is not None:
            conn.rollback()
        servicio_no_disponible()
    except Exception as e:

        if conn is not None:
            conn.rollback()
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )
    finally:
        if cur is not None:
            cur.close()
        if conn is not None:
            conn.close()

@router.get("/{id_producto}")
def obtener_producto_por_id(id_producto: int):

    conn = None
    cur = None

    try:
        conn = get_connection()
        cur = conn.cursor()

        # Buscamos el producto específico por su ID
        cur.execute(
            """
            SELECT * FROM mvg_productos()
            WHERE id_producto = %s
            """,
            (id_producto,)
        )

        row = cur.fetchone()

        if not row:
            raise HTTPException(
                status_code=404,
                detail=f"El producto con ID {id_producto} no existe"
            )

        # Retornamos el diccionario mapeado. 
        return {
            "id_producto": row[0],
            "descripcion": row[1],
            "precio": float(row[2]),
            "activo": row[3]
        }

    except psycopg2.Error:
        servicio_no_disponible()

    except HTTPException as http_err:
        raise http_err
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

    finally:
        if cur is not None:
            cur.close()
        if conn is not None:
            conn.close()
