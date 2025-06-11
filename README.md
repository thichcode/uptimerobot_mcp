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
- Tích hợp với n8n

## Yêu cầu

- Python 3.8+
- FastAPI
- UptimeRobot API Key
- Ollama (cho MCP)
- n8n (cho workflow automation)

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

## Tích hợp với n8n

### Cài đặt n8n

1. Cài đặt n8n:
```bash
npm install n8n -g
```

2. Khởi động n8n:
```bash
n8n start
```

### Tạo Workflow

1. Truy cập n8n interface tại `http://localhost:5678`

2. Tạo workflow mới và thêm các nodes:
   - HTTP Request node để gọi API
   - Function node để xử lý dữ liệu
   - Schedule Trigger node để tự động hóa
   - Email node để gửi thông báo

### Ví dụ Workflow

1. Tự động tạo maintenance window:
```json
{
  "nodes": [
    {
      "type": "n8n-nodes-base.scheduleTrigger",
      "parameters": {
        "interval": [
          {
            "field": "days",
            "value": 1
          }
        ]
      }
    },
    {
      "type": "n8n-nodes-base.httpRequest",
      "parameters": {
        "url": "http://localhost:8000/maintenance",
        "method": "POST",
        "body": {
          "start_time": "{{$now}}",
          "duration": 3600,
          "description": "Bảo trì định kỳ",
          "monitors": [123, 456]
        }
      }
    }
  ]
}
```

2. Tự động tạo báo cáo hàng tuần:
```json
{
  "nodes": [
    {
      "type": "n8n-nodes-base.scheduleTrigger",
      "parameters": {
        "interval": [
          {
            "field": "weeks",
            "value": 1
          }
        ]
      }
    },
    {
      "type": "n8n-nodes-base.httpRequest",
      "parameters": {
        "url": "http://localhost:8000/reports",
        "method": "POST",
        "body": {
          "type": "uptime",
          "start_date": "{{$now.minus(7, 'days')}}",
          "end_date": "{{$now}}"
        }
      }
    },
    {
      "type": "n8n-nodes-base.emailSend",
      "parameters": {
        "to": "admin@example.com",
        "subject": "Báo cáo uptime hàng tuần",
        "text": "{{$json}}"
      }
    }
  ]
}
```

3. Tự động xử lý sự cố:
```json
{
  "nodes": [
    {
      "type": "n8n-nodes-base.webhook",
      "parameters": {
        "path": "monitor-alert",
        "responseMode": "lastNode"
      }
    },
    {
      "type": "n8n-nodes-base.httpRequest",
      "parameters": {
        "url": "http://localhost:8000/mcp/chat",
        "method": "POST",
        "body": {
          "message": "Phân tích sự cố và đề xuất giải pháp",
          "session_id": "{{$json.session_id}}"
        }
      }
    },
    {
      "type": "n8n-nodes-base.slack",
      "parameters": {
        "channel": "#alerts",
        "text": "{{$json.ai_response.message}}"
      }
    }
  ]
}
```

### Các tính năng n8n có thể tích hợp

1. Tự động hóa:
   - Tạo maintenance window định kỳ
   - Tạo báo cáo tự động
   - Xử lý sự cố tự động

2. Thông báo:
   - Gửi email báo cáo
   - Gửi thông báo Slack/Discord
   - Gửi SMS cho sự cố nghiêm trọng

3. Tích hợp với các dịch vụ khác:
   - Jira để tạo ticket
   - Google Calendar để đồng bộ lịch
   - Grafana để hiển thị metrics

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

Xem [CONTRIBUTING.md](CONTRIBUTING.md) để biết thêm chi tiết về cách đóng góp.

## License

MIT 