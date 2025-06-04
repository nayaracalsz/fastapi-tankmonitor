from functools import wraps

from fastapi import HTTPException, Request, status

from app.utils.auth_util import get_user_from_request


def requires_role(required_role: str):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, request: Request, **kwargs):
            user = get_user_from_request(request)
            if user.role != required_role:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Access denied. Only {required_role}s allowed.",
                )
            return await func(*args, request=request, **kwargs)

        return wrapper

    return decorator
