import sys
import asyncio
import pytest
import pytest_asyncio
from typing import AsyncGenerator
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import StaticPool
from pathlib import Path

# Import from correct location
from backend.main import app
from backend.database import Base, get_db, User
from backend.auth import get_current_user_optional, get_current_user, get_password_hash

if sys.platform.startswith("win"):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

# ============================================================================
# DATABASE SETUP
# ============================================================================

TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

test_engine = create_async_engine(
    TEST_DATABASE_URL,
    echo=False,
    poolclass=StaticPool,
    connect_args={"check_same_thread": False}
)

TestAsyncSessionLocal = async_sessionmaker(
    test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

# ============================================================================
# FIXTURES
# ============================================================================

@pytest_asyncio.fixture(scope="function", autouse=True)
async def setup_database():
    """Create all database tables before EVERY test, drop after."""
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    yield
    
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture(scope="session", autouse=True)
async def setup_app():
    """
    Initialize app components that normally run on startup.
    This runs once per test session.
    """
    # Import here to avoid circular imports
    from backend.intent_classfier.classifier_class import lightWeightIntentClassifier
    import backend.main as main_module
    
    # Initialize the classifier
    classifier = lightWeightIntentClassifier(method="hybrid")
    BASE_DIR = Path(__file__).resolve().parent.parent
    MODEL_PATH = BASE_DIR / "intent_classfier" / "intentClassifier.pkl"
    
    try:
        classifier.loadModel(filepath=str(MODEL_PATH))
        print(f"✅ Classifier loaded from {MODEL_PATH}")
    except Exception as e:
        print(f"⚠️  Warning: Could not load classifier: {e}")
        # Create a dummy classifier for tests if file doesn't exist
        pass
    
    # Set the classifier in the main module
    main_module.classifier = classifier
    
    yield
    
    # Cleanup if needed
    main_module.classifier = None


@pytest_asyncio.fixture
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """Provides a test database session"""
    async with TestAsyncSessionLocal() as session:
        yield session


async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
    """Override for get_db dependency"""
    async with TestAsyncSessionLocal() as session:
        yield session


@pytest_asyncio.fixture
async def async_client() -> AsyncGenerator[AsyncClient, None]:
    """Provides an async test client with database override"""
    
    app.dependency_overrides[get_db] = override_get_db
    
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as ac:
        yield ac
    
    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def test_user(db_session: AsyncSession) -> User:
    """Creates a test user in the database"""
    user = User(
        email="testuser@example.com",
        username="testuser",
        full_name="Test User",
        hashed_password=get_password_hash("testpassword123"),
        is_active=True
    )
    
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    
    return user


@pytest_asyncio.fixture
async def auth_token(async_client: AsyncClient, test_user: User) -> str:
    """Get authentication token for test user"""
    response = await async_client.post(
        "/auth/token",
        data={
            "username": test_user.username,
            "password": "testpassword123"
        }
    )
    
    assert response.status_code == 200
    token_data = response.json()
    return token_data["access_token"]


@pytest_asyncio.fixture
async def authenticated_client(async_client: AsyncClient, auth_token: str) -> AsyncClient:
    """Provides a client with authentication headers"""
    async_client.headers.update({"Authorization": f"Bearer {auth_token}"})
    return async_client


# ============================================================================
# PYTEST CONFIGURATION
# ============================================================================

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    if sys.platform.startswith("win"):
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()