from fastapi import FastAPI, HTTPException, Header, Depends
from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime
from .models import (
    MonitorCreate, MonitorUpdate, MonitorResponse,
    MaintenanceWindow, MaintenanceResponse,
    User, UserCreate, UserUpdate, UserRole,
    Report, ReportCreate, ReportType,
    AIRequest, AIResponse, MCPResponse
)
from .services import (
    get_monitors, create_monitor, delete_monitor, update_monitor,
    get_monitor_uptime, create_maintenance_window,
    get_maintenance_windows, delete_maintenance_window
)
from .ai_processor import AIProcessor
from .mcp_context import MCPContext
from .auth import (
    create_user, authenticate_user, create_access_token,
    get_current_active_user, require_role
)
from .reports import ReportGenerator
from .cache import cache_manager

app = FastAPI(
    title="UptimeRobot MCP API",
    description="API quản lý UptimeRobot với khả năng xử lý ngôn ngữ tự nhiên"
)

ai_processor = AIProcessor()
mcp_context = MCPContext()

# Authentication endpoints
@app.post("/auth/register", response_model=User)
async def register(user: UserCreate):
    """Đăng ký người dùng mới"""
    return create_user(user)

@app.post("/auth/token")
async def login(email: str, password: str):
    """Đăng nhập và lấy token"""
    user = authenticate_user(email, password)
    if not user:
        raise HTTPException(
            status_code=401,
            detail="Email hoặc mật khẩu không đúng"
        )
    access_token = create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}

# Monitor endpoints
@app.get("/monitors", response_model=List[MonitorResponse])
async def list_monitors(
    current_user: User = Depends(require_role(UserRole.VIEWER))
):
    """Lấy danh sách tất cả monitors"""
    return await get_monitors()

@app.post("/monitors", response_model=MonitorResponse)
async def add_monitor(
    monitor: MonitorCreate,
    current_user: User = Depends(require_role(UserRole.MANAGER))
):
    """Tạo monitor mới"""
    return await create_monitor(monitor)

@app.delete("/monitors/{monitor_id}")
async def remove_monitor(
    monitor_id: int,
    current_user: User = Depends(require_role(UserRole.MANAGER))
):
    """Xóa monitor theo ID"""
    return await delete_monitor(monitor_id)

@app.put("/monitors/{monitor_id}", response_model=MonitorResponse)
async def modify_monitor(
    monitor_id: int,
    monitor: MonitorUpdate,
    current_user: User = Depends(require_role(UserRole.MANAGER))
):
    """Cập nhật monitor"""
    return await update_monitor(monitor_id, monitor)

@app.get("/monitors/{monitor_id}/uptime")
async def monitor_uptime(
    monitor_id: int,
    current_user: User = Depends(require_role(UserRole.VIEWER))
):
    """Lấy thông tin uptime của monitor"""
    return await get_monitor_uptime(monitor_id)

# Maintenance endpoints
@app.post("/maintenance", response_model=MaintenanceResponse)
async def create_maintenance(
    maintenance: MaintenanceWindow,
    current_user: User = Depends(require_role(UserRole.MANAGER))
):
    """Tạo maintenance window cho một hoặc nhiều monitors"""
    try:
        result = await create_maintenance_window(maintenance)
        return MaintenanceResponse(
            id=result["results"][0]["id"],
            start_time=maintenance.start_time,
            duration=maintenance.duration,
            description=maintenance.description,
            affected_monitors=result["affected_monitors"],
            status="success"
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/maintenance", response_model=List[MaintenanceResponse])
async def list_maintenance(
    monitor_id: Optional[int] = None,
    current_user: User = Depends(require_role(UserRole.VIEWER))
):
    """Lấy danh sách maintenance windows"""
    windows = await get_maintenance_windows(monitor_id)
    return [
        MaintenanceResponse(
            id=w["id"],
            start_time=datetime.fromtimestamp(w["start_time"]),
            duration=w["duration"],
            description=w["description"],
            affected_monitors=[w["monitor_id"]],
            status=w["status"]
        )
        for w in windows
    ]

@app.delete("/maintenance/{window_id}")
async def remove_maintenance(
    window_id: int,
    current_user: User = Depends(require_role(UserRole.MANAGER))
):
    """Xóa maintenance window"""
    return await delete_maintenance_window(window_id)

# Report endpoints
@app.post("/reports", response_model=Report)
async def generate_report(
    report_create: ReportCreate,
    current_user: User = Depends(require_role(UserRole.VIEWER))
):
    """Tạo báo cáo mới"""
    report = await ReportGenerator.generate_report(report_create)
    report.created_by = current_user.id
    return report

@app.get("/reports/{report_id}", response_model=Report)
async def get_report(
    report_id: int,
    current_user: User = Depends(require_role(UserRole.VIEWER))
):
    """Lấy thông tin báo cáo"""
    # TODO: Implement get report from database
    pass

# Cache management endpoints
@app.get("/cache/stats")
async def get_cache_stats(
    current_user: User = Depends(require_role(UserRole.ADMIN))
):
    """Lấy thống kê cache"""
    return cache_manager.get_all_stats()

@app.delete("/cache/{cache_name}")
async def clear_cache(
    cache_name: str,
    current_user: User = Depends(require_role(UserRole.ADMIN))
):
    """Xóa cache"""
    cache = cache_manager.get_cache(cache_name)
    if cache:
        cache.clear()
        return {"message": f"Đã xóa cache {cache_name}"}
    raise HTTPException(status_code=404, detail=f"Không tìm thấy cache {cache_name}")

# MCP endpoints
@app.post("/mcp/chat")
async def mcp_chat(
    request: AIRequest,
    x_session_id: Optional[str] = Header(None),
    current_user: User = Depends(require_role(UserRole.VIEWER))
):
    """Xử lý yêu cầu ngôn ngữ tự nhiên với context"""
    session_id = x_session_id or str(uuid.uuid4())
    context = mcp_context.get_context(session_id)
    
    # Phân tích yêu cầu bằng AI
    ai_response = await ai_processor.process_request(
        request,
        session_id=session_id,
        context=context
    )
    
    # Cập nhật context
    if ai_response.context_update:
        mcp_context.update_context(session_id, ai_response.context_update)
    
    # Xử lý các action dựa trên phân tích của AI
    result = None
    if ai_response.action_type == "create":
        if ai_response.monitor:
            result = await create_monitor(ai_response.monitor)
        elif ai_response.maintenance:
            result = await create_maintenance_window(ai_response.maintenance)
    elif ai_response.action_type == "update":
        if ai_response.monitor:
            result = await update_monitor(ai_response.monitor_id, ai_response.monitor)
    elif ai_response.action_type == "delete":
        if ai_response.monitor_id:
            result = await delete_monitor(ai_response.monitor_id)
        elif ai_response.maintenance_id:
            result = await delete_maintenance_window(ai_response.maintenance_id)
    elif ai_response.action_type == "get":
        if ai_response.monitor_id:
            result = await get_monitor_uptime(ai_response.monitor_id)
        elif ai_response.maintenance_id:
            windows = await get_maintenance_windows(ai_response.maintenance_id)
            result = windows[0] if windows else None
    
    return {
        "session_id": session_id,
        "ai_response": ai_response,
        "result": result
    }

@app.delete("/mcp/context/{session_id}")
async def clear_context(
    session_id: str,
    current_user: User = Depends(require_role(UserRole.VIEWER))
):
    """Xóa context của một session"""
    mcp_context.clear_context(session_id)
    return {"message": "Context đã được xóa"} 