import os
from typing import List, Dict, Any, Optional
import httpx
from .models import MonitorCreate, MonitorUpdate, MaintenanceWindow

UPTIMEROBOT_API_URL = "https://api.uptimerobot.com/v2"
API_KEY = os.getenv("UPTIMEROBOT_API_KEY")

async def get_monitors() -> List[Dict[str, Any]]:
    """Lấy danh sách tất cả monitors"""
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{UPTIMEROBOT_API_URL}/getMonitors",
            data={"api_key": API_KEY}
        )
        data = response.json()
        return data.get("monitors", [])

async def create_monitor(monitor: MonitorCreate) -> Dict[str, Any]:
    """Tạo monitor mới"""
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{UPTIMEROBOT_API_URL}/newMonitor",
            data={
                "api_key": API_KEY,
                "friendly_name": monitor.friendly_name,
                "url": str(monitor.url),
                "type": monitor.type,
                "interval": monitor.interval
            }
        )
        return response.json()

async def delete_monitor(monitor_id: int) -> Dict[str, Any]:
    """Xóa monitor theo ID"""
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{UPTIMEROBOT_API_URL}/deleteMonitor",
            data={
                "api_key": API_KEY,
                "id": monitor_id
            }
        )
        return response.json()

async def update_monitor(monitor_id: int, monitor: MonitorUpdate) -> Dict[str, Any]:
    """Cập nhật monitor"""
    data = {"api_key": API_KEY, "id": monitor_id}
    
    if monitor.friendly_name:
        data["friendly_name"] = monitor.friendly_name
    if monitor.url:
        data["url"] = str(monitor.url)
    if monitor.type:
        data["type"] = monitor.type
    if monitor.interval:
        data["interval"] = monitor.interval

    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{UPTIMEROBOT_API_URL}/editMonitor",
            data=data
        )
        return response.json()

async def get_monitor_uptime(monitor_id: int) -> Dict[str, float]:
    """Lấy thông tin uptime của monitor"""
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{UPTIMEROBOT_API_URL}/getMonitors",
            data={
                "api_key": API_KEY,
                "monitors": monitor_id,
                "custom_uptime_ranges": "1-7-30"
            }
        )
        data = response.json()
        monitor = data.get("monitors", [{}])[0]
        
        return {
            "one_day": float(monitor.get("custom_uptime_ranges", "0-0-0").split("-")[0]),
            "seven_days": float(monitor.get("custom_uptime_ranges", "0-0-0").split("-")[1]),
            "thirty_days": float(monitor.get("custom_uptime_ranges", "0-0-0").split("-")[2])
        }

async def find_monitors_by_criteria(
    tags: Optional[List[str]] = None,
    keywords: Optional[List[str]] = None
) -> List[Dict[str, Any]]:
    """Tìm monitors theo tags hoặc từ khóa"""
    all_monitors = await get_monitors()
    matched_monitors = []

    for monitor in all_monitors:
        # Kiểm tra tags
        if tags:
            monitor_tags = monitor.get("tags", [])
            if not any(tag in monitor_tags for tag in tags):
                continue

        # Kiểm tra từ khóa trong tên hoặc URL
        if keywords:
            monitor_text = f"{monitor['friendly_name']} {monitor['url']}".lower()
            if not any(keyword.lower() in monitor_text for keyword in keywords):
                continue

        matched_monitors.append(monitor)

    return matched_monitors

async def create_maintenance_window(maintenance: MaintenanceWindow) -> Dict[str, Any]:
    """Tạo maintenance window cho các monitors"""
    # Tìm monitors cần bảo trì
    affected_monitors = []
    
    if maintenance.monitors:
        affected_monitors.extend(maintenance.monitors)
    
    if maintenance.tags or maintenance.keywords:
        matched_monitors = await find_monitors_by_criteria(
            tags=maintenance.tags,
            keywords=maintenance.keywords
        )
        affected_monitors.extend([m["id"] for m in matched_monitors])

    if not affected_monitors:
        raise ValueError("Không tìm thấy monitors nào phù hợp")

    # Tạo maintenance window cho từng monitor
    results = []
    async with httpx.AsyncClient() as client:
        for monitor_id in affected_monitors:
            response = await client.post(
                f"{UPTIMEROBOT_API_URL}/newMaintenanceWindow",
                data={
                    "api_key": API_KEY,
                    "monitor_id": monitor_id,
                    "start_time": int(maintenance.start_time.timestamp()),
                    "duration": maintenance.duration,
                    "description": maintenance.description
                }
            )
            results.append(response.json())

    return {
        "affected_monitors": affected_monitors,
        "results": results
    }

async def get_maintenance_windows(monitor_id: Optional[int] = None) -> List[Dict[str, Any]]:
    """Lấy danh sách maintenance windows"""
    async with httpx.AsyncClient() as client:
        data = {"api_key": API_KEY}
        if monitor_id:
            data["monitor_id"] = monitor_id

        response = await client.post(
            f"{UPTIMEROBOT_API_URL}/getMaintenanceWindows",
            data=data
        )
        return response.json().get("maintenance_windows", [])

async def delete_maintenance_window(window_id: int) -> Dict[str, Any]:
    """Xóa maintenance window"""
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{UPTIMEROBOT_API_URL}/deleteMaintenanceWindow",
            data={
                "api_key": API_KEY,
                "id": window_id
            }
        )
        return response.json() 