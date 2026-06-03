import jwt
from datetime import datetime, timedelta
from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer

SECRET_KEY = "5c845695640692b72efc434e26533c11"
ALGORITHM = "HS256"

security = HTTPBearer()


# Crear token JWT
def crear_token(data: dict):

    data_copy = data.copy()

    data_copy["exp"] = (
        datetime.utcnow()
        + timedelta(minutes=30)
    )

    token = jwt.encode(
        data_copy,
        SECRET_KEY,
        algorithm=ALGORITHM
    )

    return token


# Validar token JWT
def validar_token(
    credentials=Depends(security)
):

    try:

        payload = jwt.decode(
            credentials.credentials,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )

        return payload

    except jwt.ExpiredSignatureError:

        raise HTTPException(
            status_code=401,
            detail="Token expirado"
        )

    except jwt.InvalidTokenError:

        raise HTTPException(
            status_code=401,
            detail="Token inválido"
        )