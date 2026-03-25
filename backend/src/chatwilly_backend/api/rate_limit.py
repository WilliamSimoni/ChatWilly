from fastapi import HTTPException, Request
from pyrate_limiter import (
    Limiter,
)


def get_client_ip(request: Request) -> str:
    cf_ip = request.headers.get("CF-Connecting-IP")
    if cf_ip:
        return cf_ip.strip()
    x_forwarded = request.headers.get("X-Forwarded-For")
    if x_forwarded:
        return x_forwarded.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


class RateLimit:
    def __init__(self, timeout: int):
        self.timeout = timeout

    def _get_bucket(self, endpoint_path: str):
        if endpoint_path == "/chat":
            return "chat_rate_limit_bucket"
        elif endpoint_path == "/token":
            return "token_rate_limit_bucket"
        return None

    async def __call__(self, request: Request):
        bucket_name = self._get_bucket(request.url.path)
        if not bucket_name:
            return
        bucket = request.app.state[bucket_name]
        client_id = f"{get_client_ip(request)}"
        with Limiter(bucket) as limiter:
            success = await limiter.try_acquire_async(client_id, timeout=self.timeout)
            if not success:
                retry_after = self.rate.interval / 1000
                raise HTTPException(
                    status_code=429,
                    detail="Too many requests",
                    headers={"Retry-After": str(int(retry_after))},
                )
