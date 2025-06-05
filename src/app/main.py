from fastapi import FastAPI

from app.api import router
from app.auth.exception_handlers import auth_exception_handlers
from app.core import config
from app.core.exception_handlers import add_exception_handlers
from app.core.lifespan import lifespan
from app.users.exception_handlers import add_user_exception_handlers

app = FastAPI(lifespan=lifespan, debug=config.APP_DEBUG)

app.include_router(router)

add_exception_handlers(app)
add_user_exception_handlers(app)
auth_exception_handlers(app)
