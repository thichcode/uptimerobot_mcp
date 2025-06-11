from pydantic import BaseModel, HttpUrl, EmailStr
from typing import Optional, Literal, List, Dict, Any
from datetime import datetime
from enum import Enum

class MonitorType(str, Enum):
    HTTP = "1"
    KEYWORD = "2"
    PING = "3"
    PORT = "4"

class MonitorBase(BaseModel):
    """Base model cho monitor"""
    friendly_name: str
    url: HttpUrl
    type: MonitorType
    interval: int = 300  # Mặc định 5 phút

class MonitorCreate(BaseModel):
    """Model để tạo monitor mới"""
    friendly_name: str
    url: HttpUrl
    type: MonitorType
    interval: int = 300

class MonitorUpdate(BaseModel):
    """Model để cập nhật monitor"""
    friendly_name: Optional[str] = None
    url: Optional[HttpUrl] = None
    type: Optional[MonitorType] = None
    interval: Optional[int] = None

class MonitorResponse(BaseModel):
    """Model response cho monitor"""
    id: int
    friendly_name: str
    url: str
    type: str
    interval: int
    status: str
    uptime: Optional[float] = None

    class Config:
        from_attributes = True

class UptimeStats(BaseModel):
    """Model cho thống kê uptime"""
    one_day: float
    seven_days: float
    thirty_days: float

class MaintenanceWindow(BaseModel):
    """Model cho maintenance window"""
    start_time: datetime
    duration: int  # Thời gian bảo trì tính bằng giây
    description: str
    monitors: Optional[List[int]] = None  # Danh sách ID monitors
    tags: Optional[List[str]] = None  # Danh sách tags
    keywords: Optional[List[str]] = None  # Danh sách từ khóa tìm kiếm

class MaintenanceResponse(BaseModel):
    """Model response cho maintenance window"""
    id: int
    start_time: datetime
    duration: int
    description: str
    affected_monitors: List[int]
    status: str  # active, completed, cancelled

class UserRole(str, Enum):
    ADMIN = "admin"
    MANAGER = "manager"
    VIEWER = "viewer"

class User(BaseModel):
    id: int
    email: EmailStr
    name: str
    role: UserRole
    created_at: datetime
    last_login: Optional[datetime] = None

class UserCreate(BaseModel):
    email: EmailStr
    name: str
    password: str
    role: UserRole = UserRole.VIEWER

class UserUpdate(BaseModel):
    name: Optional[str] = None
    password: Optional[str] = None
    role: Optional[UserRole] = None

class ReportType(str, Enum):
    UPTIME = "uptime"
    MAINTENANCE = "maintenance"
    PERFORMANCE = "performance"

class Report(BaseModel):
    id: int
    type: ReportType
    start_date: datetime
    end_date: datetime
    data: Dict[str, Any]
    created_by: int
    created_at: datetime

class ReportCreate(BaseModel):
    type: ReportType
    start_date: datetime
    end_date: datetime
    filters: Optional[Dict[str, Any]] = None

class CacheConfig(BaseModel):
    ttl: int  # Time to live in seconds
    max_size: int  # Maximum number of items
    strategy: str  # Cache strategy (LRU, FIFO, etc.)

class CacheStats(BaseModel):
    hits: int
    misses: int
    size: int
    last_updated: datetime

class MCPContext(BaseModel):
    session_id: str
    conversation_history: List[Dict[str, Any]]
    current_state: Dict[str, Any]
    metadata: Dict[str, Any]
    created_at: datetime
    last_updated: datetime

class MCPContextUpdate(BaseModel):
    conversation_history: Optional[List[Dict[str, Any]]] = None
    current_state: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None

class AIRequest(BaseModel):
    message: str
    session_id: Optional[str] = None
    context: Optional[MCPContext] = None

class AIResponse(BaseModel):
    action_type: str
    message: str
    monitor_id: Optional[int] = None
    monitor: Optional[MonitorCreate] = None
    maintenance_id: Optional[int] = None
    maintenance: Optional[MaintenanceWindow] = None
    context_update: Optional[MCPContextUpdate] = None

class MCPResponse(BaseModel):
    session_id: str
    ai_response: AIResponse
    result: Optional[Dict[str, Any]] = None 