from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Float
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base, relationship
import asyncpg
import logging
from datetime import datetime
import os
from dotenv import load_dotenv
from urllib.parse import quote
import asyncio
from pathlib import Path
load_dotenv(dotenv_path=Path(__file__).resolve().parent / ".env")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

POSTGRES_USER = os.getenv("POSTGRES_USER")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")
POSTGRES_HOST = os.getenv("POSTGRES_HOST")
POSTGRES_PORT = os.getenv("POSTGRES_PORT")
DATABASE_NAME = os.getenv("DATABASE_NAME")
FINAL_PASSWORD = quote(POSTGRES_PASSWORD)

ADMIN_DATABASE_URL = f"postgresql+asyncpg://{POSTGRES_USER}:{FINAL_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/postgres"
DATABASE_URL = f"postgresql+asyncpg://{POSTGRES_USER}:{FINAL_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{DATABASE_NAME}"

Base = declarative_base()
engine = create_async_engine(DATABASE_URL, echo = True)
SessionLocal = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, nullable = False, index = True, unique = True)
    username = Column(String, nullable = False, index = True, unique = True)
    full_name = Column(String, nullable = False)
    hashed_password = Column(String, nullable = False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default = datetime.utcnow)
    updated_at = Column(DateTime, default = datetime.utcnow, onupdate = datetime.utcnow)

    transactions = relationship("Transaction", back_populates="user", cascade="all, delete-orphan")
    budgets = relationship("Budget", back_populates = "user", cascade = "all, delete-orphan")

class Transaction(Base):
    __tablename__ = "transactions" 

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))

    reference_code = Column(String, index=True)
    date_time = Column(DateTime, nullable=False)
    description = Column(String, nullable=False)

    amount = Column(Float, nullable=False)
    type = Column(String, nullable=False)

    status = Column(String, default="Complete")
    balance = Column(Float)
    channel = Column(String)
    category = Column(String)

    user = relationship("User", back_populates="transactions")

class Budget(Base):
    __tablename__ = "budgets"

    id = Column(Integer, primary_key = True, index = True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete = "CASCADE"))

    month = Column(String, nullable = False)
    allocated = Column(Float, nullable = False)
    forecast = Column(Float, nullable = False)
    category = Column(String, nullable = False)

    user = relationship("User", back_populates = "budgets")

class ChatHistory(Base):
    __tablename__ = "chat_history"

    id = Column(Integer, primary_key = True, index = True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable = True)

    role = Column(String, nullable=False)
    text = Column(String, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)

async def create_database():
    try:
        admin_conn = await asyncpg.connect(f"postgresql://{POSTGRES_USER}:{FINAL_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/postgres")
    
        db_exists = await admin_conn.fetchval(
            "SELECT 1 FROM pg_database WHERE datname = $1", DATABASE_NAME
        )
    
        if not db_exists:
            await admin_conn.execute(f"CREATE DATABASE {DATABASE_NAME}")
            logger.info(f"Database {DATABASE_NAME} already created!!")
    
        else:
            logger.info(f"Database {DATABASE_NAME} already exists!!")
    
        await admin_conn.close()

    except Exception as e:
        logger.error(f"Error creating database {e}")
        raise

async def create_tables():
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Database tables created!!")

    except Exception as e:
        logger.error("Tables could not be created!!")
        raise

async def db_setup():
    await create_database()
    await create_tables()

async def get_db():
    async with SessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()

if __name__ == "__main__":
    asyncio.run(db_setup())