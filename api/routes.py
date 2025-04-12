from fastapi import APIRouter, Request, WebSocket, Depends, Query, HTTPException, WebSocketDisconnect
from fastapi.responses import JSONResponse
from jose import jwt, JWTError
from datetime import datetime, timezone, timedelta 

from owlchat.config import SECRET_KEY, ALGORITHM 


router = APIRouter() 


class WebSocketManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []
    
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket) 

    async def broadcast(self, user_name: str, user_token: str, message: str):
        for connections in self.active_connections:
            await connections.send_json({"user_name": user_name, "user_token": user_token, "message": message})

manager = WebSocketManager()
            
def get_auth_token(raw_token: str = Query(...)):
    try:
        token = jwt.decode(raw_token, SECRET_KEY, algorithms=[ALGORITHM])
        user_name = token['sub']
        if user_name is None:
            raise HTTPException(status_code=1008, detail="invalid credentials")
        return {'user_name': user_name, 'user_token': raw_token}
    except JWTError:
        raise HTTPException(status_code=1008, detail="invalid credentials") 
    

@router.websocket("/socket") 
async def chat_socket(websocket: WebSocket, user_data: str = Depends(get_auth_token)):
    user_name = user_data['user_name']
    user_token = user_data['user_token']
    await manager.connect(websocket) 
    try:
        while True:
            data = await websocket.receive_text()
            await manager.broadcast(user_name, user_token, data)
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    