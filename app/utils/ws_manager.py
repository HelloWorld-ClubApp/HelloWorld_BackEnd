# WebSocket 연결 관리 (채팅 접속자 관리)
# 작성자 : 엄인섭
from fastapi import WebSocket
from typing import List, Dict

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[int, List[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, room_id: int):
        await websocket.accept()
        if room_id not in self.active_connections:
            self.active_connections[room_id] = []
        self.active_connections[room_id].append(websocket)

    def disconnect(self, websocket: WebSocket, room_id: int):
        if room_id in self.active_connections:
            if websocket in self.active_connections[room_id]:
                self.active_connections[room_id].remove(websocket)

    async def broadcast(self, message: str, room_id: int):
        if room_id in self.active_connections:
            # 1. 안전하게 순회하기 위해 리스트를 복사 (혹은 필터링)
            # 연결이 끊긴 소켓을 저장할 리스트
            dead_connections = []
            
            for connection in self.active_connections[room_id]:
                try:
                    await connection.send_text(message)
                except Exception:
                    # 2. 메시지 전송 실패 시, 해당 연결은 끊긴 것으로 간주하고 목록에 추가
                    dead_connections.append(connection)
            
            # 3. 죽은 연결들 리스트에서 제거
            for dead_conn in dead_connections:
                self.disconnect(dead_conn, room_id)
manager = ConnectionManager()