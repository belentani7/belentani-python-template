from __future__ import annotations
from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
import time
from collections import defaultdict
from typing import Dict, Tuple

class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(
        self,
        app,
        requests_per_minute: int = 60,
        requests_per_hour: int = 1000,
        excluded_paths: list[str] = None,
    ):
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        self.requests_per_hour = requests_per_hour
        self.excluded_paths = excluded_paths or ["/health", "/docs", "/redoc", "/openapi.json"]
        self.minute_buckets: Dict[str, Tuple[int, float]] = defaultdict(lambda: (0, 0.0))
        self.hour_buckets: Dict[str, Tuple[int, float]] = defaultdict(lambda: (0, 0.0))

    def _get_client_id(self, request: Request) -> str:
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            return forwarded.split(",")[0].strip()
        return request.client.host if request.client else "unknown"

    def _is_excluded(self, path: str) -> bool:
        return any(path.startswith(excluded) for excluded in self.excluded_paths)

    def _check_limit(self, bucket: Dict[str, Tuple[int, float]], client_id: str, limit: int, window_seconds: int) -> bool:
        now = time.time()
        count, window_start = bucket[client_id]
        if now - window_start > window_seconds:
            bucket[client_id] = (1, now)
            return True
        if count >= limit:
            return False
        bucket[client_id] = (count + 1, window_start)
        return True

    async def dispatch(self, request: Request, call_next) -> Response:
        if self._is_excluded(request.url.path):
            return await call_next(request)

        client_id = self._get_client_id(request)

        minute_ok = self._check_limit(self.minute_buckets, client_id, self.requests_per_minute, 60)
        hour_ok = self._check_limit(self.hour_buckets, client_id, self.requests_per_hour, 3600)

        if not minute_ok or not hour_ok:
            retry_after = 60 if not minute_ok else 3600
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Rate limit exceeded",
                headers={"Retry-After": str(retry_after)},
            )

        response = await call_next(request)
        return response;
