from fastapi import FastAPI

from auth_dock.api import router
from auth_dock.core.lifespan import lifespan

app = FastAPI(lifespan=lifespan)

app.include_router(router)
