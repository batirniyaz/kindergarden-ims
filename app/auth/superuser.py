from app.auth.model import User, UserRole
from app.auth.util import get_password_hash
from app.db.get_db import async_session_maker
from sqlalchemy.future import select


async def create_superuser():

    async with async_session_maker() as session:
        async with session.begin():
            result = await session.execute(select(User).filter_by(email='admin@example.com'))
            superuser = result.scalars().first()

            if not superuser:
                superuser = User(
                    phone="+998999999999",
                    email="admin@example.com",
                    username='admin',
                    first_name="Super",
                    last_name="User",
                    hashed_password=get_password_hash("admin"),
                    role=UserRole.ADMIN,
                )
                session.add(superuser)
                await session.commit()
