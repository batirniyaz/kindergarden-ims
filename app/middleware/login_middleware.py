import time
import logging
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
import jwt
from jwt import PyJWTError

from app.config import SECRET, ALGORITHM
from app.db.db import async_session_maker
from app.models.action_log import ActionLog

logger = logging.getLogger("uvicorn.access")

class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()

        user_info = {
            "user_id": None,
            "email": None,
            "role": None,
            "username": None,
            "phone": None,
        }
        request.state.query = str(request.url.query)

        token = request.headers.get("Authorization")
        authorized = False
        if token and token.startswith("Bearer "):
            token = token[7:]
            try:
                payload = jwt.decode(token, SECRET, algorithms=[ALGORITHM])
                user_info["user_id"] = payload.get("user_id")
                user_info["email"] = payload.get("email")
                user_info["role"] = payload.get("role")
                user_info["username"] = payload.get("sub")
                user_info["phone"] = payload.get("phone")
                request.state.user = user_info
                authorized = True
            except PyJWTError:
                pass

        response: Response = await call_next(request)

        if authorized:
            process_time = round(time.time() - start_time, 4)

            log_data = ActionLog(
                user_id=user_info["user_id"],
                phone=user_info["phone"],
                email=user_info["email"],
                username=user_info["username"],
                role=user_info["role"],
                query=request.state.query,
                path=request.url.path,
                method=request.method,
                status_code=response.status_code,
                process_time=process_time,
                client_host=request.client.host,
            )

            async with async_session_maker() as session:
                session.add(log_data)
                await session.commit()

        return response

