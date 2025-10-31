import asyncio
from typing import Optional
from fastapi import HTTPException, Depends, status, APIRouter, Form
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel, EmailStr
from passlib.context import CryptContext
from jose import JWTError, jwt
import logging
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta
from backend.database import User, get_db
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

load_dotenv()

logging.basicConfig(level="INFO")
logger = logging.getLogger(__name__)

# Single OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")  # Changed to /token
oauth2_scheme_optional = OAuth2PasswordBearer(tokenUrl="auth/token", auto_error=False)

SECRET_KEY = os.getenv('SECRET_KEY')
ALGORITHM = os.getenv('ALGORITHM')
TOKEN_EXPIRE_TIME = int(os.getenv('TOKEN_EXPIRE_TIME', 30))

pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')

class UserCreate(BaseModel):
    email: EmailStr
    username: str
    full_name: str
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

class UserResponse(BaseModel):
    id: int
    email: str
    username: str
    full_name: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

def verifypassword(password, hashedpassword):
    return pwd_context.verify(password, hashedpassword)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict, expiredelta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expiredelta:
        expire = datetime.utcnow() + expiredelta
    else:
        expire = datetime.utcnow() + timedelta(minutes=TOKEN_EXPIRE_TIME)

    to_encode.update({"exp": expire})
    jwt_encode = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return jwt_encode

async def get_user_by_username(db: AsyncSession, username: str):
    result = await db.execute(select(User).where(User.username == username))
    return result.scalar_one_or_none()

async def get_user_by_email(db: AsyncSession, email: str):
    result = await db.execute(select(User).where(User.email == email))
    return result.scalar_one_or_none()

async def create_user(db: AsyncSession, user: UserCreate):
    hashed_password = get_password_hash(user.password)
    db_user = User(
        email=user.email,
        username=user.username,
        full_name=user.full_name,
        hashed_password=hashed_password
    )
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user

async def authenticate_user(db: AsyncSession, username: str, password: str):
    user = await get_user_by_username(db, username)
    if not user:
        return False
    if not verifypassword(password, user.hashed_password):
        return False
    return user

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"}
    )

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = await get_user_by_username(db, username)
    if user is None:
        raise credentials_exception
    return user

async def get_current_user_optional(
    token: Optional[str] = Depends(oauth2_scheme_optional),
    db: AsyncSession = Depends(get_db)
) -> Optional[User]:
    if not token:
        return None
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if not username:
            return None
        
        user = await get_user_by_username(db, username)
        return user
    except JWTError:
        return None

def get_current_active_user(user: User = Depends(get_current_user)):
    if not user.is_active:
        raise HTTPException(status_code=400, detail="User not active")
    return user

router = APIRouter()

@router.post("/register", response_model=UserResponse)
async def register_user(user: UserCreate, db: AsyncSession = Depends(get_db)):
    new_user = await get_user_by_email(db, user.email)
    if new_user:
        raise HTTPException(
            status_code=400,
            detail="User with this email already exists!!"
        )
    
    new_user = await get_user_by_username(db, user.username)
    if new_user:
        raise HTTPException(
            status_code=400,
            detail="User with username already exists!!"
        )
    
    new_user = await create_user(db, user)
    logger.info("New user registered!!")
    return new_user

@router.post("/token", response_model=Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db)
):
    """
    OAuth2 compatible token endpoint.
    Uses form data (username, password) as per OAuth2 spec.
    """
    user = await authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=TOKEN_EXPIRE_TIME)
    access_token = create_access_token(
        data={"sub": user.username}, 
        expiredelta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/login", response_model=Token)
async def loginUser(user: UserLogin, db: AsyncSession = Depends(get_db)):
    """
    JSON-based login endpoint.
    Alternative to /token for applications that prefer JSON.
    """
    log_user = await authenticate_user(db, user.username, user.password)
    if not log_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    data = {"sub": user.username}
    access_token = create_access_token(data)
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/profile", response_model=UserResponse)
async def getProfile(current_user: User = Depends(get_current_active_user)):
    return current_user