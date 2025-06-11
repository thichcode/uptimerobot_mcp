from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import pandas as pd
from .models import Report, ReportCreate, ReportType
from .services import get_monitors, get_maintenance_windows
from .cache import report_cache

class ReportGenerator:
    @staticmethod
    async def generate_uptime_report(
        start_date: datetime,
        end_date: datetime,
        filters: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Tạo báo cáo uptime"""
        cache_key = f"uptime_{start_date}_{end_date}_{str(filters)}"
        cached_report = report_cache.get(cache_key)
        if cached_report:
            return cached_report

        monitors = await get_monitors()
        report_data = {
            "total_monitors": len(monitors),
            "average_uptime": 0,
            "monitors": []
        }

        total_uptime = 0
        for monitor in monitors:
            monitor_data = {
                "id": monitor["id"],
                "name": monitor["friendly_name"],
                "url": monitor["url"],
                "uptime": monitor.get("custom_uptime_ranges", "0-0-0").split("-")[0],
                "status": monitor["status"]
            }
            report_data["monitors"].append(monitor_data)
            total_uptime += float(monitor_data["uptime"])

        if monitors:
            report_data["average_uptime"] = total_uptime / len(monitors)

        report_cache.set(cache_key, report_data)
        return report_data

    @staticmethod
    async def generate_maintenance_report(
        start_date: datetime,
        end_date: datetime,
        filters: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Tạo báo cáo maintenance"""
        cache_key = f"maintenance_{start_date}_{end_date}_{str(filters)}"
        cached_report = report_cache.get(cache_key)
        if cached_report:
            return cached_report

        windows = await get_maintenance_windows()
        report_data = {
            "total_windows": len(windows),
            "total_duration": 0,
            "windows": []
        }

        for window in windows:
            window_start = datetime.fromtimestamp(window["start_time"])
            if start_date <= window_start <= end_date:
                window_data = {
                    "id": window["id"],
                    "start_time": window_start,
                    "duration": window["duration"],
                    "description": window["description"],
                    "monitor_id": window["monitor_id"]
                }
                report_data["windows"].append(window_data)
                report_data["total_duration"] += window["duration"]

        report_cache.set(cache_key, report_data)
        return report_data

    @staticmethod
    async def generate_performance_report(
        start_date: datetime,
        end_date: datetime,
        filters: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Tạo báo cáo hiệu suất"""
        cache_key = f"performance_{start_date}_{end_date}_{str(filters)}"
        cached_report = report_cache.get(cache_key)
        if cached_report:
            return cached_report

        monitors = await get_monitors()
        report_data = {
            "total_monitors": len(monitors),
            "response_times": [],
            "status_distribution": {}
        }

        for monitor in monitors:
            # Thêm thời gian phản hồi
            if "response_times" in monitor:
                report_data["response_times"].append({
                    "monitor_id": monitor["id"],
                    "name": monitor["friendly_name"],
                    "avg_response_time": sum(monitor["response_times"]) / len(monitor["response_times"])
                })

            # Thống kê trạng thái
            status = monitor["status"]
            report_data["status_distribution"][status] = report_data["status_distribution"].get(status, 0) + 1

        report_cache.set(cache_key, report_data)
        return report_data

    @staticmethod
    async def generate_report(report_create: ReportCreate) -> Report:
        """Tạo báo cáo theo loại"""
        if report_create.type == ReportType.UPTIME:
            data = await ReportGenerator.generate_uptime_report(
                report_create.start_date,
                report_create.end_date,
                report_create.filters
            )
        elif report_create.type == ReportType.MAINTENANCE:
            data = await ReportGenerator.generate_maintenance_report(
                report_create.start_date,
                report_create.end_date,
                report_create.filters
            )
        elif report_create.type == ReportType.PERFORMANCE:
            data = await ReportGenerator.generate_performance_report(
                report_create.start_date,
                report_create.end_date,
                report_create.filters
            )
        else:
            raise ValueError(f"Loại báo cáo không hợp lệ: {report_create.type}")

        return Report(
            id=1,  # ID sẽ được tạo bởi database
            type=report_create.type,
            start_date=report_create.start_date,
            end_date=report_create.end_date,
            data=data,
            created_by=1,  # User ID sẽ được lấy từ context
            created_at=datetime.now()
        ) 