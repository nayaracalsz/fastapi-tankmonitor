from fastapi import Request
from fastapi.middleware import Middleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.middleware.cors import CORSMiddleware

ALLOWED_HOSTS_DEV = [
    "localhost",
    "127.0.0.1",
    "testserver"
]

CORS_ALLOW_ORIGINS_DEV = [
    "http://localhost:3000",
    "http://127.0.0.1:3000"
]

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        security_headers = {
            "X-Frame-Options": "DENY",
            "X-Content-Type-Options": "nosniff",
            "X-XSS-Protection": "1; mode=block",
            "Content-Security-Policy": "default-src 'self';",
            "Permissions-Policy": "geolocation=(), microphone=()",
            "Referrer-Policy": "strict-origin-when-cross-origin",
            "Strict-Transport-Security": "max-age=63072000; includeSubDomains; preload"
        }

        for header, value in security_headers.items():
            response.headers[header] = value

        return response

def get_security_middleware(is_production: bool = False):
    if is_production:
        allowed_hosts = ["*"]
        allow_origins = ["*"]
    else:
        allowed_hosts = ALLOWED_HOSTS_DEV
        allow_origins = CORS_ALLOW_ORIGINS_DEV

    return [
        Middleware(SecurityHeadersMiddleware),
        Middleware(
            TrustedHostMiddleware,
            allowed_hosts=allowed_hosts
        ),
        Middleware(
            CORSMiddleware,
            allow_origins=allow_origins,
            allow_methods=["GET", "POST", "PUT", "DELETE"],
            allow_headers=["*"],
            allow_credentials=True
        ),
        Middleware(GZipMiddleware, minimum_size=1000),
        #Middleware(HTTPSRedirectMiddleware)
    ]