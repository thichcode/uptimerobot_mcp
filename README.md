# UptimeRobot MCP API

API quản lý UptimeRobot với khả năng xử lý ngôn ngữ tự nhiên thông qua Model Context Protocol (MCP).

## Tính năng

- Quản lý monitors (tạo, cập nhật, xóa, xem)
- Quản lý maintenance windows
- Tạo báo cáo (uptime, maintenance, performance)
- Xử lý ngôn ngữ tự nhiên thông qua MCP
- Hệ thống phân quyền người dùng
- Cache management
- Context management cho MCP

## Yêu cầu

- Python 3.8+
- FastAPI
- UptimeRobot API Key
- Ollama (cho MCP)

## Cài đặt

1. Clone repository:
```bash
git clone https://github.com/thichcode/uptimerobot_mcp.git
cd uptimerobot_mcp
```

2. Tạo môi trường ảo và cài đặt dependencies:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
pip install -r requirements.txt
```

3. Cấu hình biến môi trường:
```bash
cp .env.example .env
# Chỉnh sửa .env với các thông tin cần thiết
```

## Sử dụng

1. Khởi động server:
```bash
uvicorn app.main:app --reload
```

2. Truy cập API documentation:
```
http://localhost:8000/docs
```

## API Endpoints

### Authentication
- `POST /auth/register` - Đăng ký người dùng mới
- `POST /auth/token` - Đăng nhập và lấy token

### Monitors
- `GET /monitors` - Lấy danh sách monitors
- `POST /monitors` - Tạo monitor mới
- `PUT /monitors/{monitor_id}` - Cập nhật monitor
- `DELETE /monitors/{monitor_id}` - Xóa monitor
- `GET /monitors/{monitor_id}/uptime` - Lấy thông tin uptime

### Maintenance Windows
- `POST /maintenance` - Tạo maintenance window
- `GET /maintenance` - Lấy danh sách maintenance windows
- `DELETE /maintenance/{window_id}` - Xóa maintenance window

### Reports
- `POST /reports` - Tạo báo cáo mới
- `GET /reports/{report_id}` - Lấy thông tin báo cáo

### Cache Management
- `GET /cache/stats` - Lấy thống kê cache
- `DELETE /cache/{cache_name}` - Xóa cache

### MCP
- `POST /mcp/chat` - Xử lý yêu cầu ngôn ngữ tự nhiên
- `DELETE /mcp/context/{session_id}` - Xóa context

## Ví dụ sử dụng

### Tạo monitor mới
```bash
curl -X POST "http://localhost:8000/monitors" \
     -H "Authorization: Bearer {token}" \
     -H "Content-Type: application/json" \
     -d '{
         "friendly_name": "Example Website",
         "url": "https://example.com",
         "type": "1",
         "interval": 300
     }'
```

### Tạo maintenance window
```bash
curl -X POST "http://localhost:8000/maintenance" \
     -H "Authorization: Bearer {token}" \
     -H "Content-Type: application/json" \
     -d '{
         "start_time": "2024-03-20T10:00:00Z",
         "duration": 3600,
         "description": "Bảo trì hệ thống",
         "monitors": [123, 456]
     }'
```

### Sử dụng MCP
```bash
curl -X POST "http://localhost:8000/mcp/chat" \
     -H "Authorization: Bearer {token}" \
     -H "Content-Type: application/json" \
     -d '{
         "message": "Tạo maintenance window cho tất cả các monitors có tag production vào ngày mai từ 10h đến 11h",
         "session_id": "abc123"
     }'
```

## Phân quyền

- **ADMIN**: Toàn quyền truy cập
- **MANAGER**: Quản lý monitors và maintenance windows
- **VIEWER**: Chỉ xem thông tin

## Đóng góp

Mọi đóng góp đều được hoan nghênh! Vui lòng tạo issue hoặc pull request.

## License

MIT 