from fastapi import FastAPI, Request, Depends, Query, HTTPException
from fastapi.responses import JSONResponse, HTMLResponse, RedirectResponse 
from fastapi.staticfiles import StaticFiles
from .api.routes import router as api_router
from datetime import datetime, timezone, timedelta
from jose import jwt, JWTError
from fastapi.templating import Jinja2Templates
from .config import SECRET_KEY, ALGORITHM 
from pathlib import Path 

base_dir = Path(__file__).resolve().parent 


app = FastAPI() 
templates = Jinja2Templates(directory=(f"{base_dir}/templates")) 
app.mount("/static", StaticFiles(directory=(f"{base_dir}/static")), name="static") 


@app.get("/chatroom")
async def chatroom(request: Request):
    return templates.TemplateResponse(
        "chatroom.html",
        {"request":request}
    )


def create_user_token(data: dict):
    expiration = datetime.now(timezone.utc) + timedelta(hours=3)
    data = data.copy()
    data.update({"exp": expiration})
    return jwt.encode(data,SECRET_KEY,algorithm=ALGORITHM)


@app.route("/", methods=['GET','POST'])  # response_class=HTMLResponse
async def index(request: Request): 
    if request.method == 'POST': 
        body = await request.json()
        data = {"sub": body['username']}
        token = create_user_token(data)
        return JSONResponse(content={"token":token})
    return templates.TemplateResponse(
        "index.html",
        {"request": request}
    )


app.include_router(api_router, prefix="/api")