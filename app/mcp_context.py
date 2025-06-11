from typing import Dict, Any, List, Optional
from datetime import datetime
import json
from pydantic import BaseModel

class ContextState(BaseModel):
    """Model cho trạng thái context"""
    session_id: str
    created_at: datetime
    last_updated: datetime
    conversation_history: List[Dict[str, Any]]
    current_state: Dict[str, Any]
    metadata: Dict[str, Any]

class MCPContext:
    def __init__(self):
        """Khởi tạo MCP Context Manager"""
        self.contexts: Dict[str, ContextState] = {}
        self.max_history_length = 10

    def create_context(self, session_id: str) -> ContextState:
        """Tạo context mới cho session"""
        now = datetime.now()
        context = ContextState(
            session_id=session_id,
            created_at=now,
            last_updated=now,
            conversation_history=[],
            current_state={},
            metadata={}
        )
        self.contexts[session_id] = context
        return context

    def get_context(self, session_id: str) -> Optional[ContextState]:
        """Lấy context theo session_id"""
        return self.contexts.get(session_id)

    def update_context(self, session_id: str, 
                      message: Dict[str, Any],
                      state_update: Optional[Dict[str, Any]] = None,
                      metadata_update: Optional[Dict[str, Any]] = None) -> ContextState:
        """Cập nhật context với message mới"""
        context = self.get_context(session_id)
        if not context:
            context = self.create_context(session_id)

        # Cập nhật lịch sử hội thoại
        context.conversation_history.append({
            "timestamp": datetime.now().isoformat(),
            "message": message
        })
        
        # Giới hạn độ dài lịch sử
        if len(context.conversation_history) > self.max_history_length:
            context.conversation_history = context.conversation_history[-self.max_history_length:]

        # Cập nhật state
        if state_update:
            context.current_state.update(state_update)

        # Cập nhật metadata
        if metadata_update:
            context.metadata.update(metadata_update)

        context.last_updated = datetime.now()
        return context

    def get_conversation_summary(self, session_id: str) -> str:
        """Tạo tóm tắt cuộc hội thoại"""
        context = self.get_context(session_id)
        if not context:
            return ""

        summary = []
        for entry in context.conversation_history:
            summary.append(f"{entry['timestamp']}: {json.dumps(entry['message'])}")
        
        return "\n".join(summary)

    def clear_context(self, session_id: str) -> None:
        """Xóa context của session"""
        if session_id in self.contexts:
            del self.contexts[session_id] 