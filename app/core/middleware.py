from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from core.config import settings
import time
from collections import defaultdict
import asyncio

# Simple in-memory rate limiter (use Redis in production)
rate_limit_store = defaultdict(list)

class RateLimitMiddleware:
    def __init__(self, requests_per_minute: int = 100):
        self.requests_per_minute = requests_per_minute

    async def __call__(self, request: Request, call_next):
        # Get client IP
        client_ip = request.client.host
        
        # Check rate limit
        current_time = time.time()
        minute_ago = current_time - 60
        
        # Clean old requests
        rate_limit_store[client_ip] = [
            req_time for req_time in rate_limit_store[client_ip] 
            if req_time > minute_ago
        ]
        
        # Check if limit exceeded
        if len(rate_limit_store[client_ip]) >= self.requests_per_minute:
            return JSONResponse(
                status_code=429,
                content={
                    "success": False,
                    "error": "rate_limit_exceeded",
                    "message": "تعداد درخواست‌ها بیش از حد مجاز است",
                    "retry_after": 60
                }
            )
        
        # Add current request
        rate_limit_store[client_ip].append(current_time)
        
        # Continue with request
        response = await call_next(request)
        return response

class CORSMiddleware:
    def __init__(self, app):
        self.app = app

    async def __call__(self, request: Request, call_next):
        response = await call_next(request)
        
        # Add CORS headers
        response.headers["Access-Control-Allow-Origin"] = "*"
        response.headers["Access-Control-Allow-Credentials"] = "true"
        response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
        response.headers["Access-Control-Allow-Headers"] = "Authorization, Content-Type"
        
        return response

class ErrorHandlingMiddleware:
    async def __call__(self, request: Request, call_next):
        try:
            response = await call_next(request)
            return response
        except HTTPException as e:
            return JSONResponse(
                status_code=e.status_code,
                content={
                    "success": False,
                    "error": "http_error",
                    "message": e.detail,
                    "status_code": e.status_code
                }
            )
        except Exception as e:
            return JSONResponse(
                status_code=500,
                content={
                    "success": False,
                    "error": "internal_server_error",
                    "message": "خطای داخلی سرور",
                    "details": str(e) if settings.DEBUG else None
                }
            ) 