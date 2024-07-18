import hashlib
import uuid
from datetime import datetime
from datetime import timedelta
from datetime import timezone
from typing import Dict
from typing import Tuple

import jwt
from core.config import settings
from crud.refresh_session_crud import create_or_update_refresh_session
from fastapi import Header
from jwt import DecodeError
from jwt import ExpiredSignatureError
from pydantic import EmailStr
from schemas.user import UserSchema
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status
from starlette.exceptions import HTTPException
from starlette.requests import Request
from starlette.responses import Response

ACCESS_TOKEN_TYPE = 'access'
REFRESH_TOKEN_TYPE = 'refresh'

FAKE_DB = [
    {
        'email': 'user@example.com',
        'password': 'string',
    },
]


def encode_jwt(
    token_type: str,
    payload: dict,
    private_key: str = settings.jwt_settings.private_key.read_text(),
    algorithm: str = settings.jwt_settings.algorithm,
    expire_minutes: int = settings.jwt_settings.access_token_expire_minutes,
    expire_timedelta: timedelta | None = None,
) -> str:
    to_encode = payload.copy()
    now = datetime.now(tz=timezone.utc)
    expire = now + (
        expire_timedelta if expire_timedelta else timedelta(minutes=expire_minutes)
    )
    to_encode.update(
        token_type=token_type, exp=expire, iat=now, jit=str(uuid.uuid4().hex)
    )
    return jwt.encode(to_encode, private_key, algorithm=algorithm)


def decode_jwt(
    token: str | bytes,
    public_key: str = settings.jwt_settings.public_key.read_text(),
    algorithm: str = settings.jwt_settings.algorithm,
) -> dict:
    try:
        return jwt.decode(token, public_key, algorithms=[algorithm])
    except ExpiredSignatureError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail='Token is expired'
        ) from e
    except DecodeError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail='Token is invalid'
        ) from e


def create_access_token(payload: Dict) -> str:
    return encode_jwt(
        token_type=ACCESS_TOKEN_TYPE,
        payload=payload,
        expire_minutes=settings.jwt_settings.access_token_expire_minutes,
    )


def create_refresh_token(payload: Dict) -> str:
    return encode_jwt(
        token_type=REFRESH_TOKEN_TYPE,
        payload=payload,
        expire_timedelta=timedelta(
            days=settings.jwt_settings.refresh_token_expire_days
        ),
    )


def generate_fingerprint(unique_string: str) -> str:
    return hashlib.sha256(unique_string.encode()).hexdigest()


def check_password(user: UserSchema):
    user_db = FAKE_DB[0]
    if user.model_dump() != user_db:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Email or password incorrect',
        )


async def handle_refresh_session(
    session: AsyncSession, decoded_refresh_token: dict, request: Request
):
    ip = request.client.host
    user_agent = request.headers.get('user-agent', 'unknown')
    fingerprint = generate_fingerprint(f'{ip}-{user_agent}')
    data_refresh_session_create = {
        'user_email': decoded_refresh_token.get('email'),
        'refresh_token_jit': decoded_refresh_token.get('jit'),
        'user_agent': user_agent,
        'ip': ip,
        'fingerprint': fingerprint,
        'expires': decoded_refresh_token.get('exp'),
    }
    await create_or_update_refresh_session(session, data_refresh_session_create)


def set_refresh_token_cookie(
    response: Response, refresh_token: str, decoded_refresh_token: dict
):
    response.set_cookie(
        key='refresh_token',
        value=refresh_token,
        domain=settings.domain,
        path='/api/v1/auth',
        max_age=decoded_refresh_token.get('exp'),
        httponly=True,
    )


async def create_pair_tokens(
    request: Request,
    response: Response,
    user: UserSchema,
    session: AsyncSession,
) -> Dict[str, str]:
    check_password(user)
    payload = user.model_dump(exclude={'password'})
    access_token, refresh_token, decoded_refresh_token = await generate_tokens(
        payload, request, session
    )
    set_refresh_token_cookie(response, refresh_token, decoded_refresh_token)
    return {
        'access_token': access_token,
    }


async def update_pair_tokens(
    request: Request,
    response: Response,
    refresh_token: str,
    session: AsyncSession,
) -> Dict[str, str]:
    try:
        decoded_token = decode_jwt(refresh_token)
    except jwt.PyJWTError as err:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail='Token is invalid'
        ) from err

    if decoded_token.get('token_type') != REFRESH_TOKEN_TYPE:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Token isn't refresh"
        )

    payload = {'email': decoded_token.get('email')}
    access_token, new_refresh_token, decoded_refresh_token = await generate_tokens(
        payload, request, session
    )
    set_refresh_token_cookie(response, new_refresh_token, decoded_refresh_token)
    return {
        'access_token': access_token,
    }


async def generate_tokens(
    payload: Dict, request: Request, session: AsyncSession
) -> Tuple:
    access_token = create_access_token(payload)
    refresh_token = create_refresh_token(payload)
    decoded_refresh_token = decode_jwt(refresh_token)
    await handle_refresh_session(session, decoded_refresh_token, request)
    return access_token, refresh_token, decoded_refresh_token


async def get_my_email(authorization: str = Header()) -> EmailStr:
    decoded_token = decode_jwt(authorization)
    if decoded_token.get('token_type') != ACCESS_TOKEN_TYPE:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Token isn't {ACCESS_TOKEN_TYPE}",
        )
    return decoded_token.get('email')
