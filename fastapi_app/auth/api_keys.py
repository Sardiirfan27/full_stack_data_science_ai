import redis.asyncio as aioredis
import os
import uuid
from fastapi import Header, HTTPException

REDIS_HOST = os.getenv("REDIS_HOST")
REDIS_PORT = int(os.getenv("REDIS_PORT"))
REDIS_DB = int(os.getenv("REDIS_DB"))

cache = aioredis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB, decode_responses=True)

async def generate_api_key():
    """Generate a new API key and store in Redis set"""
    key = str(uuid.uuid4())
    await cache.sadd("api_keys_allowed", key)
    return key

async def validate_api_key(api_key: str = Header(...)):
    """
    Validate API key against Redis set 'api_keys_allowed'.
    Raise HTTP 401 if invalid.
    """
    is_valid = await cache.sismember("api_keys_allowed", api_key)
    if not is_valid:
        raise HTTPException(status_code=401, detail="Invalid API key")
    return api_key
