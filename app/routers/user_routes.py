from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from app.models import User
from app.models import Package
from app.models import async_session
from app.core.config import settings
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
from pydantic import BaseModel
from typing import Optional, List

router = APIRouter(prefix="/users/api/auth",tags=["users"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/users/api/auth/login")


async def get_db() -> AsyncSession:
    async with async_session() as session:
        yield session


class LoginRequest(BaseModel):
    email: str
    password: str


class UserCreate(BaseModel):
    email: str
    password: str
    phone: Optional[str] = None
    full_name: Optional[str] = None
    is_courier: Optional[bool] = False


class UserUpdate(BaseModel):
    email: Optional[str] = None
    phone: Optional[str] = None
    full_name: Optional[str] = None
    password: Optional[str] = None
    is_courier: Optional[bool] = None


class UserOut(BaseModel):
    id: int
    email: str
    phone: Optional[str]
    full_name: Optional[str]
    is_courier: bool
    created_at: datetime

    class Config:
        orm_mode = True


class PackageCreate(BaseModel):
    tracking_number: str
    destination_pvz: str
    user_id: int


class PackageOut(BaseModel):
    tracking_number: str
    destination_pvz: str
    status: str

    class Config:
        orm_mode = True


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

SECRET_KEY = settings.SECRET_KEY
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = (await db.execute(select(User).where(User.email == email))).scalars().first()
    if user is None:
        raise credentials_exception
    return user


async def get_current_admin_user(current_user: User = Depends(get_current_user)):
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="The user doesn't have enough privileges"
        )
    return current_user


@router.post("/login")
async def login(request: LoginRequest, db: AsyncSession = Depends(get_db)):
    user = (await db.execute(select(User).where(User.email == request.email))).scalars().first()
    if not user or not pwd_context.verify(request.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Incorrect email or password")

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data={"sub": user.email}, expires_delta=access_token_expires)
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/register", status_code=status.HTTP_201_CREATED, response_model=UserOut)
async def register(user: UserCreate, db: AsyncSession = Depends(get_db)):
    db_user = (await db.execute(select(User).where(User.email == user.email))).scalars().first()
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    hashed_password = pwd_context.hash(user.password)
    new_user = User(
        email=user.email,
        hashed_password=hashed_password,
        phone=user.phone,
        full_name=user.full_name,
        is_courier=user.is_courier
    )

    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return new_user


@router.get("/me", response_model=UserOut)
async def read_current_user(current_user: User = Depends(get_current_user)):
    return current_user


@router.patch("/me", response_model=UserOut)
async def update_current_user(
        user_data: UserUpdate,
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    update_data = user_data.dict(exclude_unset=True)

    if "password" in update_data:
        current_user.hashed_password = pwd_context.hash(update_data.pop("password"))

    for field, value in update_data.items():
        setattr(current_user, field, value)

    db.add(current_user)
    await db.commit()
    await db.refresh(current_user)
    return current_user


@router.get("/", response_model=List[UserOut])
async def read_users(
        skip: int = 0,
        limit: int = 100,
        current_user: User = Depends(get_current_admin_user),
        db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(User).offset(skip).limit(limit))
    return result.scalars().all()


@router.get("/couriers", response_model=List[UserOut])
async def read_couriers(
        skip: int = 0,
        limit: int = 100,
        db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(User)
        .where(User.is_courier == True)
        .offset(skip)
        .limit(limit)
    )
    return result.scalars().all()


@router.post("/packages/", response_model=PackageOut, status_code=status.HTTP_201_CREATED)
async def create_package(
    package_data: PackageCreate,
    db: AsyncSession = Depends(get_db)
):
    """Создание новой посылки"""
    new_package = Package(
        tracking_number=package_data.tracking_number,
        destination_pvz=package_data.destination_pvz,
        status="created",
    )
    db.add(new_package)
    await db.commit()
    await db.refresh(new_package)
    return new_package

@router.get("/packages/{tracking_number}", response_model=PackageOut)
async def get_package(
    tracking_number: str,
    db: AsyncSession = Depends(get_db)
):
    """Получение информации о посылке"""
    package = await db.execute(
        select(Package).where(Package.tracking_number == tracking_number)
    )
    package = package.scalars().first()
    if not package:
        raise HTTPException(status_code=404, detail="Package not found")
    return package