from fastapi import (
    APIRouter,
    HTTPException,
    Depends
)

from pydantic import BaseModel
from typing import Optional

from app.core.security import validar_token

import csv
import os
import re


router = APIRouter(
    prefix="/v1/clientes",
    tags=["Clientes V1"],
    dependencies=[Depends(validar_token)]
)

ARCH_CLIENTES = "data/clientes.csv"


# ======================================================
# FUNCIONES CSV
# ======================================================

def inicializar_archivo():

    if not os.path.exists(
        ARCH_CLIENTES
    ):

        with open(
            ARCH_CLIENTES,
            mode="w",
            newline="",
            encoding="utf-8"
        ) as f:

            writer = csv.writer(f)

            writer.writerow([
                "id_cliente",
                "nombre",
                "correo",
                "telefono",
                "direccion",
                "fecha_registro",
                "activo"
            ])


def leer_clientes():

    inicializar_archivo()

    clientes = []

    with open(
        ARCH_CLIENTES,
        mode="r",
        newline="",
        encoding="utf-8"
    ) as f:

        reader = csv.DictReader(f)

        for row in reader:

            row["id_cliente"] = int(
                row["id_cliente"]
            )

            row["activo"] = (
                row["activo"] == "True"
            )

            row["fecha_registro"] = (
                row.get(
                    "fecha_registro"
                )
                or "2024-01-01"
            )

            clientes.append(row)

    return clientes


def guardar_clientes(
    clientes
):

    with open(
        ARCH_CLIENTES,
        mode="w",
        newline="",
        encoding="utf-8"
    ) as f:

        campos = [
            "id_cliente",
            "nombre",
            "correo",
            "telefono",
            "direccion",
            "fecha_registro",
            "activo"
        ]

        writer = csv.DictWriter(
            f,
            fieldnames=campos
        )

        writer.writeheader()
        writer.writerows(
            clientes
        )


def es_correo_valido(
    correo
):

    return re.match(
        r'^[\w\.-]+@[\w\.-]+\.\w+$',
        correo
    ) is not None


# ======================================================
# MODELOS
# ======================================================

class ClienteCreate(
    BaseModel
):
    nombre: str
    correo: str
    telefono: Optional[
        str
    ] = ""

    direccion: Optional[
        str
    ] = ""


class ClienteUpdate(
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


class ClienteDelete(
    BaseModel
):
    id_cliente: int


# ======================================================
# ENDPOINTS V1
# ======================================================

@router.get("/")
def obtener_clientes():

    clientes = leer_clientes()

    return [
        c for c in clientes
        if c["activo"]
    ]


@router.post(
    "/",
    status_code=201
)
def crear_cliente(
    cliente:
    ClienteCreate
):

    clientes = leer_clientes()

    if (
        len(
            cliente.nombre
        ) < 3
        or not
        es_correo_valido(
            cliente.correo
        )
    ):
        raise HTTPException(
            status_code=400,
            detail=(
                "Formato de "
                "nombre o "
                "correo inválido"
            )
        )

    for c in clientes:

        if (
            c["activo"]
            and
            c["correo"].lower()
            ==
            cliente.correo.lower()
        ):
            raise HTTPException(
                status_code=400,
                detail=(
                    "El correo ya "
                    "está registrado"
                )
            )

    nuevo_id = max(
        [
            c["id_cliente"]
            for c in clientes
        ],
        default=0
    ) + 1

    nuevo_cliente = {

        "id_cliente":
        nuevo_id,

        "nombre":
        cliente.nombre,

        "correo":
        cliente.correo,

        "telefono":
        cliente.telefono,

        "direccion":
        cliente.direccion,

        "fecha_registro":
        "2024-01-01",

        "activo":
        True
    }

    clientes.append(
        nuevo_cliente
    )

    guardar_clientes(
        clientes
    )

    return {
        "mensaje":
        "Cliente registrado",

        "datos":
        nuevo_cliente
    }


@router.patch("/")
def modificar_cliente(
    cliente:
    ClienteUpdate
):

    clientes = leer_clientes()

    for c in clientes:

        if (
            c["id_cliente"]
            ==
            cliente.id_cliente
            and
            c["activo"]
        ):

            if cliente.nombre:
                c["nombre"] = (
                    cliente.nombre
                )

            if cliente.telefono:
                c["telefono"] = (
                    cliente.telefono
                )

            if cliente.direccion:
                c["direccion"] = (
                    cliente.direccion
                )

            if cliente.correo:

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

                for otro in clientes:

                    if (
                        otro[
                            "id_cliente"
                        ]
                        !=
                        c[
                            "id_cliente"
                        ]
                        and
                        otro[
                            "activo"
                        ]
                        and
                        otro[
                            "correo"
                        ].lower()
                        ==
                        cliente.correo.lower()
                    ):
                        raise HTTPException(
                            status_code=400,
                            detail=(
                                "Correo en uso"
                            )
                        )

                c["correo"] = (
                    cliente.correo
                )

            guardar_clientes(
                clientes
            )

            return {
                "mensaje":
                "Cliente modificado",
                "datos":
                c
            }

    raise HTTPException(
        status_code=404,
        detail=(
            "Cliente no encontrado"
        )
    )


@router.delete("/")
def eliminar_cliente(
    cliente:
    ClienteDelete
):

    clientes = leer_clientes()

    for c in clientes:

        if (
            c["id_cliente"]
            ==
            cliente.id_cliente
            and
            c["activo"]
        ):

            c["activo"] = False

            guardar_clientes(
                clientes
            )

            return {
                "mensaje":
                "Cliente "
                "deshabilitado "
                "exitosamente"
            }

    raise HTTPException(
        status_code=404,
        detail=(
            "Cliente no encontrado"
        )
    )