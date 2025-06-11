# Hướng dẫn đóng góp

Cảm ơn bạn đã quan tâm đến việc đóng góp cho dự án UptimeRobot MCP API! Dưới đây là một số hướng dẫn để giúp bạn bắt đầu.

## Quy trình đóng góp

1. Fork repository
2. Tạo branch mới (`git checkout -b feature/amazing-feature`)
3. Commit thay đổi (`git commit -m 'Add some amazing feature'`)
4. Push lên branch (`git push origin feature/amazing-feature`)
5. Tạo Pull Request

## Quy tắc code

- Tuân thủ PEP 8 cho Python code
- Thêm docstring cho tất cả các hàm và class
- Viết unit test cho các tính năng mới
- Cập nhật documentation khi thêm tính năng mới

## Cấu trúc dự án

```
uptimerobot_mcp/
├── app/
│   ├── __init__.py
│   ├── main.py          # FastAPI application
│   ├── models.py        # Pydantic models
│   ├── services.py      # Business logic
│   ├── auth.py          # Authentication
│   ├── cache.py         # Cache management
│   ├── reports.py       # Report generation
│   ├── ai_processor.py  # MCP processing
│   └── mcp_context.py   # Context management
├── tests/               # Unit tests
├── docs/               # Documentation
└── examples/           # Example code
```

## Cài đặt môi trường phát triển

1. Clone repository:
```bash
git clone https://github.com/thichcode/uptimerobot_mcp.git
cd uptimerobot_mcp
```

2. Tạo môi trường ảo:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

3. Cài đặt dependencies:
```bash
pip install -r requirements.txt
pip install -r requirements-dev.txt  # Development dependencies
```

4. Cấu hình pre-commit hooks:
```bash
pre-commit install
```

## Chạy tests

```bash
pytest
```

## Tạo documentation

```bash
cd docs
make html
```

## Quy tắc commit message

Sử dụng format sau cho commit messages:
```
<type>(<scope>): <subject>

<body>

<footer>
```

Types:
- feat: Tính năng mới
- fix: Sửa lỗi
- docs: Thay đổi documentation
- style: Formatting, thiếu semicolons, etc
- refactor: Refactoring code
- test: Thêm tests
- chore: Cập nhật build process, etc

## Pull Request Process

1. Cập nhật README.md với chi tiết về thay đổi nếu cần
2. Tăng version number trong bất kỳ file nào thay đổi
3. Pull Request sẽ được merge sau khi có ít nhất 1 review approval

## Báo cáo lỗi

Sử dụng GitHub Issues để báo cáo lỗi. Vui lòng bao gồm:
- Mô tả chi tiết về lỗi
- Steps to reproduce
- Expected behavior
- Actual behavior
- Screenshots nếu có
- Environment details

## Đề xuất tính năng

Sử dụng GitHub Issues để đề xuất tính năng mới. Vui lòng bao gồm:
- Mô tả chi tiết về tính năng
- Use cases
- Implementation suggestions
- Screenshots/mockups nếu có

## Code of Conduct

- Tôn trọng người khác
- Chấp nhận constructive criticism
- Tập trung vào vấn đề, không phải cá nhân
- Hỗ trợ người khác

## License

Bằng cách đóng góp, bạn đồng ý rằng đóng góp của bạn sẽ được cấp phép theo MIT License. 