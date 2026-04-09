import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.pool import NullPool
from sqlalchemy import event

from app.main import app
from app.database import get_db
from app.models import Base, User
from app.auth.user_auth import get_current_user

TEST_DATABASE_URL = "postgresql+asyncpg://postgres:Qwerty123@localhost:5432/test_db"


@pytest.fixture(scope="session")
async def engine():
    engine = create_async_engine(
        TEST_DATABASE_URL,
        echo=False,
        poolclass=NullPool,
    )

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()


@pytest.fixture
async def db_session(engine):
    async with engine.connect() as conn:
        outer = await conn.begin()

        async_session_factory = async_sessionmaker(
            bind=conn,
            class_=AsyncSession,
            expire_on_commit=False,
        )

        async with async_session_factory() as session:
            await session.begin_nested()

            @event.listens_for(session.sync_session, "after_transaction_end")
            def _restart_savepoint(sess, trans):
                if trans.nested and not sess.in_nested_transaction():
                    sess.begin_nested()

            try:
                yield session
            finally:
                await session.close()
                await outer.rollback()


@pytest.fixture
async def db(db_session):
    return db_session


@pytest.fixture
async def user(db_session):
    u = User(
        telegram_id=1234567890,
        username="test_user",
        is_admin=True,
        is_active=True,
    )
    db_session.add(u)
    await db_session.flush()
    await db_session.refresh(u)
    return u


@pytest.fixture
async def async_client(db_session):
    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://testserver",
    ) as client:
        yield client

    app.dependency_overrides.pop(get_db, None)


@pytest.fixture
async def authorized_client(async_client, user):
    async def override_get_current_user():
        return user

    app.dependency_overrides[get_current_user] = override_get_current_user
    try:
        yield async_client
    finally:
        app.dependency_overrides.pop(get_current_user, None)


@pytest.fixture
async def client(authorized_client):
    return authorized_client