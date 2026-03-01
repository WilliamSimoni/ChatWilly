import logging
import uvicorn
from chatwilly_backend.settings import global_settings
from chatwilly_backend.api.routes import router
from chatwilly_backend.api.lifespan import lifespan
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

logging.basicConfig(level=logging.DEBUG if global_settings.debug else logging.INFO)
logger = logging.getLogger("chatwilly")

app = FastAPI(
    title=global_settings.app_name,
    version=global_settings.app_version,
    debug=global_settings.debug,
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # ⚠️ To restrict to specific origins, replace "*" with a list of allowed origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=global_settings.app_port,
        reload=True if global_settings.debug else False
    )