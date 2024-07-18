from typing import Dict

from models.refresh_session import RefreshSession
from sqlalchemy import delete
from sqlalchemy import insert
from sqlalchemy import select
from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession


async def create_or_update_refresh_session(
    session: AsyncSession,
    data: Dict,
) -> int:
    stmt = select(RefreshSession).where(
        RefreshSession.fingerprint == data.get('fingerprint')
    )
    existing_session = await session.scalar(stmt)

    if existing_session:
        stmt = (
            update(RefreshSession)
            .where(RefreshSession.fingerprint == data.get('fingerprint'))
            .values(**data)
            .returning(RefreshSession.id)
        )
        result = await session.scalar(stmt)
    else:
        stmt = insert(RefreshSession).values(**data).returning(RefreshSession.id)
        result = await session.scalar(stmt)

    await session.commit()

    stmt = select(RefreshSession).where(
        RefreshSession.user_email == data.get('user_email')
    )
    if len((await session.scalars(stmt)).all()) > 5:
        stmt = delete(RefreshSession).where(
            RefreshSession.refresh_token != data.get('refresh_token')
        )
        await session.execute(stmt)
        await session.commit()

    return result
