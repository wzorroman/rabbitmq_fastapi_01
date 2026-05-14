# api/api_server.py
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import APP_HOST, APP_PORT
from fastapi import FastAPI
from api.routers import rout_publicaciones

app = FastAPI(title="Integrador Dluxor API")
app.include_router(rout_publicaciones.router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=APP_HOST, port=APP_PORT)

