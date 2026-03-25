import uuid
from datetime import datetime, timedelta, timezone

import httpx
import jwt
from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from chatwilly_backend.settings import global_settings

bearer_scheme = HTTPBearer()


def create_conversation_token() -> str:
    payload = {
        "conversation_id": str(uuid.uuid4()),
        "exp": datetime.now(timezone.utc)
        + timedelta(minutes=global_settings.token_ttl_minutes),
        "iat": datetime.now(timezone.utc),
    }
    return jwt.encode(
        payload, global_settings.jwt_secret, algorithm=global_settings.token_algorithm
    )


def decode_token(token: str) -> dict:
    try:
        return jwt.decode(
            token,
            global_settings.jwt_secret,
            algorithms=[global_settings.token_algorithm],
        )
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")


async def verify_turnstile(turnstile_token: str) -> None:
    if not global_settings.turnstile_enabled:
        return

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                "https://challenges.cloudflare.com/turnstile/v0/siteverify",
                data={
                    "secret": global_settings.turnstile_secret_token,
                    "response": turnstile_token,
                },
                timeout=10,
            )
            response.raise_for_status()
            result = response.json()
        except httpx.RequestError:
            raise HTTPException(
                status_code=503, detail="Turnstile verification unavailable"
            )

    if not result.get("success"):
        raise HTTPException(status_code=403, detail="Turnstile verification failed")


async def get_conversation_id(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
) -> str:
    """FastAPI dependency — validates JWT and returns conversation_id."""
    payload = decode_token(credentials.credentials)
    return payload["conversation_id"]
