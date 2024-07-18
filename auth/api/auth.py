from db.db_helper import get_db_session
from fastapi import APIRouter
from fastapi import Cookie
from fastapi import Depends
from schemas.jwt_token import TokenSchema
from schemas.user import UserEmailSchema
from schemas.user import UserSchema
from services.token import create_pair_tokens
from services.token import get_my_email
from services.token import update_pair_tokens
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.requests import Request
from starlette.responses import Response

router = APIRouter(prefix='/auth')


@router.post('/login', response_model=TokenSchema)
async def login(
    request: Request,
    response: Response,
    user: UserSchema,
    session: AsyncSession = Depends(get_db_session),
):
    return await create_pair_tokens(request, response, user, session)


@router.post('/refresh-token', response_model=TokenSchema)
async def refresh_token(
    request: Request,
    response: Response,
    refresh_token: str = Cookie(),
    session: AsyncSession = Depends(get_db_session),
):
    return await update_pair_tokens(request, response, refresh_token, session)


@router.post('/protected', response_model=UserEmailSchema)
async def get_info_about_met(user_email: UserSchema = Depends(get_my_email)):
    return UserEmailSchema(email=user_email)
