import asyncio
import logging
logger = logging.getLogger(__name__)

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
    phone: str
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
    weight: Optional[float] = None
    price: Optional[float] = None
    from_address: Optional[str] = None
    urgency: Optional[str] = None


class PackageOut(BaseModel):
    id: int
    tracking_number: str
    destination_pvz: str
    from_address: Optional[str]
    weight: Optional[float]
    price: Optional[float]
    urgency: Optional[str]
    status: str
    created_at: datetime

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
    user = (await db.execute(select(User).where(User.phone == request.phone))).scalars().first()
    if not user or not pwd_context.verify(request.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Incorrect phone or password")

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data={"sub": user.email}, expires_delta=access_token_expires)
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/register", status_code=status.HTTP_201_CREATED, response_model=UserOut)
async def register(user: UserCreate, db: AsyncSession = Depends(get_db)):
    db_user = (await db.execute(select(User).where(User.phone == user.phone))).scalars().first()
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
        user_id=package_data.user_id,
        status="created",
        weight=package_data.weight,
        price=package_data.price,
        from_address=package_data.from_address,
        urgency=package_data.urgency
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


# Добавим в user_routes.py

class PackageUpdate(BaseModel):
    status: str


@router.put("/packages/{tracking_number}/pay", response_model=PackageOut)
async def pay_package(
        tracking_number: str,
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    package = await db.execute(
        select(Package).where(Package.tracking_number == tracking_number)
    )
    package = package.scalars().first()
    if not package:
        raise HTTPException(status_code=404, detail="Package not found")

    package.status = "paid"
    package.user_id = current_user.id
    await db.commit()
    await db.refresh(package)

    # Запускаем задачу для автоматического перехода в processing
    asyncio.create_task(schedule_processing_status(package.id))

    return package


@router.get("/packages/", response_model=List[PackageOut])
async def get_user_packages(
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    """Получение всех посылок пользователя"""
    result = await db.execute(
        select(Package)
        .where(Package.user_id == current_user.id)
        .order_by(Package.created_at.desc())
    )
    return result.scalars().all()


# Добавьте новые модели для статусов
class PackageStatusUpdate(BaseModel):
    status: str


# Автоматический переход paid → processing (планировщик)
async def schedule_processing_status(package_id: int):
    await asyncio.sleep(10)  # Ждем 10 секунд (для теста)
    async with async_session() as db:
        async with db.begin():
            package = await db.get(Package, package_id)
            if package and package.status == "paid":
                package.status = "processing"
                await db.commit()
    logger.info(f"Checking package {package_id} for status update")
    if package and package.status == "paid":
        logger.info(f"Updating package {package_id} to processing")

# Эндпоинты для изменения статусов
@router.put("/packages/{tracking_number}/status", response_model=PackageOut)
async def update_package_status(
        tracking_number: str,
        status_data: PackageStatusUpdate,
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    """Обновление статуса посылки (для админов и курьеров)"""
    package = await db.execute(
        select(Package).where(Package.tracking_number == tracking_number)
    )
    package = package.scalars().first()

    if not package:
        raise HTTPException(status_code=404, detail="Package not found")

    # Проверка прав (админ или курьер)
    if not (current_user.is_admin or current_user.is_courier):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins and couriers can update status"
        )

    # Валидация переходов статусов
    valid_transitions = {
        "created": ["paid"],
        "paid": ["processing"],
        "processing": ["shipped"],
        "shipped": ["delivered"],
        "delivered": ["completed"]
    }

    if (package.status in valid_transitions and
            status_data.status in valid_transitions[package.status]):
        package.status = status_data.status

        # Если перешли в paid, планируем переход в processing
        if status_data.status == "paid":
            asyncio.create_task(schedule_processing_status(package.id, db))

        await db.commit()
        await db.refresh(package)
        return package
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid status transition from {package.status} to {status_data.status}"
        )


# Эндпоинт для получения всех посылок (для админов/курьеров)
@router.get("/admin/packages/", response_model=List[PackageOut])
async def get_all_packages(
        status: Optional[str] = None,
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    """Получение всех посылок (для админов и курьеров)"""
    if not (current_user.is_admin or current_user.is_courier):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins and couriers can view all packages"
        )

    query = select(Package)
    if status:
        query = query.where(Package.status == status)

    result = await db.execute(query.order_by(Package.created_at.desc()))
    return result.scalars().all()

@router.get("/")
def home():
    return {"message": "QUICK PARCEL API is working!"}