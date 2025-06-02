from fastapi import FastAPI

from app.api import router
from app.core.exception_handlers import add_exception_handlers
from app.core.lifespan import lifespan

app = FastAPI(lifespan=lifespan)

app.include_router(router)
add_exception_handlers(app)
