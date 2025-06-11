import json
import requests
from typing import Dict, Any, List, Optional
from pydantic import BaseModel
from .mcp_context import MCPContext

class AIRequest(BaseModel):
    """Model cho yêu cầu AI"""
    prompt: str
    session_id: str
    model: str = "llama2"
    context: Optional[Dict[str, Any]] = None

class AIResponse(BaseModel):
    """Model cho phản hồi AI"""
    response: str
    action: Dict[str, Any]
    confidence: float
    context_update: Optional[Dict[str, Any]] = None

class AIProcessor:
    def __init__(self, ollama_url: str = "http://localhost:11434"):
        """Khởi tạo AI Processor với Ollama API"""
        self.ollama_url = ollama_url.rstrip('/')
        self.context_manager = MCPContext()
        self.system_prompt = """Bạn là một trợ lý AI chuyên phân tích yêu cầu người dùng về quản lý UptimeRobot.
        Bạn có khả năng duy trì context và thực hiện các hành động phức tạp qua nhiều bước.
        
        Hãy phân tích yêu cầu và trả về JSON với format sau:
        {
            "action": {
                "type": "create|update|delete|get|multi_step",
                "monitor_id": null,  # ID của monitor nếu có
                "data": {  # Dữ liệu cần thiết cho action
                    "friendly_name": null,
                    "url": null,
                    "type": null,
                    "interval": null
                },
                "steps": []  # Các bước thực hiện cho multi_step
            },
            "context_update": {  # Cập nhật context nếu cần
                "state": {},
                "metadata": {}
            },
            "confidence": 0.95  # Độ tin cậy của phân tích (0-1)
        }
        """

    def _build_prompt(self, request: AIRequest) -> str:
        """Xây dựng prompt với context"""
        context = self.context_manager.get_context(request.session_id)
        if not context:
            return f"{self.system_prompt}\n\nUser: {request.prompt}\nAssistant:"

        # Thêm tóm tắt cuộc hội thoại
        conversation_summary = self.context_manager.get_conversation_summary(request.session_id)
        current_state = json.dumps(context.current_state, indent=2)
        
        return f"""{self.system_prompt}

Lịch sử hội thoại:
{conversation_summary}

Trạng thái hiện tại:
{current_state}

User: {request.prompt}
Assistant:"""

    def _call_ollama(self, prompt: str, model: str = "llama2") -> str:
        """Gọi Ollama API"""
        try:
            response = requests.post(
                f"{self.ollama_url}/api/generate",
                json={
                    "model": model,
                    "prompt": prompt,
                    "stream": False
                }
            )
            response.raise_for_status()
            return response.json()["response"]
        except Exception as e:
            raise Exception(f"Lỗi khi gọi Ollama API: {str(e)}")

    def _parse_ai_response(self, response: str) -> Dict[str, Any]:
        """Phân tích phản hồi từ AI"""
        try:
            # Tìm JSON trong phản hồi
            start_idx = response.find('{')
            end_idx = response.rfind('}') + 1
            if start_idx == -1 or end_idx == 0:
                raise ValueError("Không tìm thấy JSON trong phản hồi")
            
            json_str = response[start_idx:end_idx]
            return json.loads(json_str)
        except Exception as e:
            raise Exception(f"Lỗi khi phân tích phản hồi AI: {str(e)}")

    async def process_request(self, request: AIRequest) -> AIResponse:
        """Xử lý yêu cầu từ user"""
        try:
            # Xây dựng prompt với context
            prompt = self._build_prompt(request)
            
            # Gọi Ollama API
            ai_response = self._call_ollama(prompt, request.model)
            
            # Phân tích phản hồi
            parsed_response = self._parse_ai_response(ai_response)
            
            # Cập nhật context
            if parsed_response.get("context_update"):
                self.context_manager.update_context(
                    request.session_id,
                    {"prompt": request.prompt, "response": ai_response},
                    parsed_response["context_update"].get("state"),
                    parsed_response["context_update"].get("metadata")
                )
            
            return AIResponse(
                response=ai_response,
                action=parsed_response["action"],
                confidence=parsed_response["confidence"],
                context_update=parsed_response.get("context_update")
            )
        except Exception as e:
            raise Exception(f"Lỗi khi xử lý yêu cầu: {str(e)}")

    async def analyze_monitor_request(self, request: str, session_id: str) -> Dict[str, Any]:
        """Phân tích yêu cầu liên quan đến monitor"""
        ai_request = AIRequest(prompt=request, session_id=session_id)
        response = await self.process_request(ai_request)
        return response.action

    def clear_context(self, session_id: str) -> None:
        """Xóa context của session"""
        self.context_manager.clear_context(session_id) 