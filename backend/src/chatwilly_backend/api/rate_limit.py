from fastapi import HTTPException, Request


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

    def _get_limiter(self, endpoint_path):
        if endpoint_path == "/chat":
            return "chat_rate_limiter"
        else:
            return None

    async def __call__(self, request: Request):
        limiter_name = self._get_limiter(request.url.path)
        if not limiter_name:
            return
        limiter = request.app.state[limiter_name]
        client_id = f"{get_client_ip(request)}"
        success = await limiter.try_acquire_async(client_id, timeout=self.timeout)
        if not success:
            retry_after = self.rate.interval / 1000
            raise HTTPException(
                status_code=429,
                detail="Too many requests",
                headers={"Retry-After": str(int(retry_after))},
            )
