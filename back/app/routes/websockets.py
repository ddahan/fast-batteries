from fastapi import APIRouter, WebSocket, WebSocketDisconnect

router = APIRouter(prefix="/ws", tags=["WebSockets"])


connected_clients: list[WebSocket] = []


@router.websocket("/broadcast-message")
async def broadcast_message(websocket: WebSocket):
    await websocket.accept()
    connected_clients.append(websocket)
    try:
        while True:
            data = await websocket.receive_json()
            sender = data["name"]
            message = data["message"]
            for client in connected_clients:
                await client.send_json({"name": sender, "message": message})
    except WebSocketDisconnect:
        connected_clients.remove(websocket)
