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

from app.core.security import validar_token
from app.core.db import get_connection


router = APIRouter(
    prefix="/v2",
    tags=["Inventario V2"],
    dependencies=[Depends(validar_token)]
)


# ======================================================
# MODELOS
# ======================================================

class InventarioUpdateV2(
    BaseModel
):

    id_producto: int = Field(
        ...,
        example=1
    )

    cantidad: int = Field(
        ...,
        example=5
    )
    
class DescuentoInventario(BaseModel):
    id_producto: int
    cantidad: int


def servicio_no_disponible():
    raise HTTPException(
        status_code=503,
        detail="Servicio de inventario no disponible"
    )


# ======================================================
# ENDPOINTS V2
# ======================================================

@router.get("/inventario")
def reporte_inventario_v2():

    conn = None
    cur = None

    try:

        conn = get_connection()
        cur = conn.cursor()

        cur.execute(
            "SELECT * "
            "FROM "
            "mvg_inventario()"
        )

        rows = cur.fetchall()

        inventario = []

        for row in rows:

            inventario.append({

                "id_producto":
                row[0],

                "cantidad":
                row[1]
            })

        return {
            "total_productos":
            len(inventario),

            "inventario":
            inventario
        }

    except psycopg2.Error:

        servicio_no_disponible()

    finally:

        if cur is not None:
            cur.close()

        if conn is not None:
            conn.close()


@router.patch("/inventario")
def modificar_inventario_v2(
    data:
    InventarioUpdateV2
):

    if data.cantidad <= 0:

        raise HTTPException(
            status_code=400,
            detail="Cantidad inválida"
        )

    conn = None
    cur = None

    try:

        conn = get_connection()
        cur = conn.cursor()

        cur.execute(
            """
            CALL
            mvg_inventario_modificar(
                %s,%s
            )
            """,
            (
                data.id_producto,
                data.cantidad
            )
        )

        conn.commit()

        return {
            "mensaje":
            "Inventario actualizado"
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

@router.delete("/inventario/desc")
def descontar_inventario(
    data: DescuentoInventario 
):
    if data.cantidad <= 0:
        raise HTTPException(
            status_code=400,
            detail="La cantidad a restar debe ser mayor a cero"
        )

    conn = None
    cur = None

    try:
        conn = get_connection()
        cur = conn.cursor()

        cur.execute(
            """
            CALL mvg_inventario_descontar(
                %s, %s
            )
            """,
            (
                data.id_producto,
                data.cantidad
            )
        )

        conn.commit()

        return {
            "mensaje": f"Se descontaron {data.cantidad} unidades del inventario"
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

