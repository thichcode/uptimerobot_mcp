from typing import Optional
from datetime import datetime, timedelta
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from .models import User, UserCreate, UserRole

# Cấu hình
SECRET_KEY = "your-secret-key"  # Nên được lưu trong biến môi trường
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Khởi tạo
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Giả lập database
users_db = {}

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Xác thực mật khẩu"""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Tạo hash cho mật khẩu"""
    return pwd_context.hash(password)

def create_user(user: UserCreate) -> User:
    """Tạo người dùng mới"""
    if user.email in users_db:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email đã tồn tại"
        )

    hashed_password = get_password_hash(user.password)
    db_user = User(
        id=len(users_db) + 1,
        email=user.email,
        name=user.name,
        role=user.role,
        created_at=datetime.now(),
        last_login=None
    )
    users_db[user.email] = {
        "user": db_user,
        "hashed_password": hashed_password
    }
    return db_user

def authenticate_user(email: str, password: str) -> Optional[User]:
    """Xác thực người dùng"""
    user_data = users_db.get(email)
    if not user_data:
        return None
    if not verify_password(password, user_data["hashed_password"]):
        return None
    
    user = user_data["user"]
    user.last_login = datetime.now()
    return user

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Tạo access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    """Lấy thông tin người dùng hiện tại từ token"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Không thể xác thực thông tin đăng nhập",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user_data = users_db.get(email)
    if user_data is None:
        raise credentials_exception
    
    return user_data["user"]

def check_permission(user: User, required_role: UserRole) -> bool:
    """Kiểm tra quyền của người dùng"""
    role_hierarchy = {
        UserRole.ADMIN: 3,
        UserRole.MANAGER: 2,
        UserRole.VIEWER: 1
    }
    return role_hierarchy[user.role] >= role_hierarchy[required_role]

async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """Kiểm tra người dùng đang hoạt động"""
    if not current_user:
        raise HTTPException(status_code=400, detail="Người dùng không hoạt động")
    return current_user

def require_role(required_role: UserRole):
    """Decorator để yêu cầu quyền cụ thể"""
    async def role_checker(current_user: User = Depends(get_current_active_user)):
        if not check_permission(current_user, required_role):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Không đủ quyền truy cập"
            )
        return current_user
    return role_checker 