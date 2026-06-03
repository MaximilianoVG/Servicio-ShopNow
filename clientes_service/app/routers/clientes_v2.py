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
import re
import psycopg2

from app.core.security import validar_token
from app.core.db import get_connection

router = APIRouter(
    prefix="/v2/clientes",
    tags=["Clientes V2"]
)

# ======================================================
# MODELOS
# ======================================================

class ClienteCreateV2(
    BaseModel
):

    nombre: str = Field(
        ...,
        example="Juan Escutia"
    )
    correo: str = Field(
        ...,
        example="juan@email.com"
    )
    telefono: str = Field(
        ...,
        example="4421234567"
    )
    direccion: str = Field(
        ...,
        example="Querétaro"
    )


class ClienteUpdateV2(
    BaseModel
):

    id_cliente: int

    nombre: Optional[
        str
    ] = None

    correo: Optional[
        str
    ] = None

    telefono: Optional[
        str
    ] = None

    direccion: Optional[
        str
    ] = None

    activo: Optional[
        bool
    ] = None
    


class ClienteDeleteV2(
    BaseModel
):
    id_cliente: int

# ======================================================
# VALIDACIÓN
# ======================================================

def es_correo_valido(
    correo
):

    return re.match(
        r'^[\w\.-]+@[\w\.-]+\.\w+$',
        correo
    ) is not None


def servicio_no_disponible():
    raise HTTPException(
        status_code=503,
        detail="Servicio de clientes no disponible"
    )


# ======================================================
# ENDPOINTS V2
# ======================================================

@router.get("/",
    dependencies=[Depends(validar_token)])
def obtener_clientes():

    conn = None
    cur = None

    try:

        conn = get_connection()
        cur = conn.cursor()

        cur.execute(
            "SELECT * FROM mvg_clientes()"
        )

        rows = cur.fetchall()

        clientes = []

        for row in rows:

            clientes.append({
                "id_cliente":
                row[0],
                "nombre":
                row[1],
                "correo":
                row[2],
                "direccion":
                row[3],
                "telefono":
                row[4],
                "activo":
                row[5]
            })

        return {
            "total_clientes":
            len(clientes),

            "clientes":
            clientes
        }

    except psycopg2.Error:
        servicio_no_disponible()

    finally:
        if cur is not None:
            cur.close()

        if conn is not None:
            conn.close()


@router.post(
    "/",
    status_code=201,
    dependencies=[Depends(validar_token)]
)
def crear_cliente(
    cliente:
    ClienteCreateV2
):

    if (
        not
        cliente.telefono.isdigit()
        or
        len(
            cliente.telefono
        ) < 7
    ):
        raise HTTPException(
            status_code=400,
            detail=(
                "Teléfono inválido"
            )
        )

    if (
        len(
            cliente.nombre
        ) < 5
    ):
        raise HTTPException(
            status_code=400,
            detail=(
                "El nombre "
                "debe tener "
                "al menos "
                "5 caracteres"
            )
        )

    if not (
        es_correo_valido(
            cliente.correo
        )
    ):
        raise HTTPException(
            status_code=400,
            detail=(
                "Correo inválido"
            )
        )

    conn = None
    cur = None

    try:

        conn = get_connection()
        cur = conn.cursor()

        cur.execute(
            """
            CALL
            mvg_clientes_insertar(
                %s,%s,%s,%s
            )
            """,
            (
                cliente.nombre,
                cliente.correo,
                cliente.direccion,
                cliente.telefono
            )
        )

        conn.commit()

        return {
            "mensaje":
            "Cliente "
            "registrado "
            "correctamente"
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
dependencies=[Depends(validar_token)]
)
def modificar_cliente(
    cliente:
    ClienteUpdateV2
):

    conn = None
    cur = None

    try:

        conn = get_connection()
        cur = conn.cursor()

        cur.execute(
            """
            CALL
            mvg_clientes_modificar(
                %s,%s,%s,%s,%s,%s
            )
            """,
            (
                cliente.id_cliente,
                cliente.nombre,
                cliente.correo,
                cliente.direccion,
                cliente.telefono,
                cliente.activo
            )
        )

        conn.commit()

        return {
            "mensaje":
            "Cliente "
            "actualizado "
            "correctamente"
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
dependencies=[Depends(validar_token)]
)
def eliminar_cliente(
    cliente:
    ClienteDeleteV2
):

    conn = None
    cur = None

    try:

        conn = get_connection()
        cur = conn.cursor()

        cur.execute(
            """
            CALL
            mvg_clientes_eliminar(
                %s
            )
            """,
            (
                cliente.id_cliente,
            )
        )

        conn.commit()

        return {
            "mensaje":
            "Cliente eliminado"
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

@router.get("/{id_cliente}")
def obtener_cliente_por_id(id_cliente: int):

    conn = None
    cur = None

    try:
        conn = get_connection()
        cur = conn.cursor()

        # Buscamos únicamente al cliente con el ID solicitado
        cur.execute(
            """
            SELECT id_cliente, nombre, correo, direccion, telefono, activo 
            FROM clientes 
            WHERE id_cliente = %s
            """,
            (id_cliente,)
        )

        row = cur.fetchone()

        # Si la base de datos no regresa nada, mandamos un 404 real
        if not row:
            raise HTTPException(
                status_code=404,
                detail=f"El cliente con ID {id_cliente} no existe en la base de datos"
            )

        # Si existe, devolvemos sus datos en un diccionario
        return {
            "id_cliente": row[0],
            "nombre": row[1],
            "correo": row[2],
            "direccion": row[3],
            "telefono": row[4],
            "activo": row[5]
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
