from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from schema import PredictRequest, PredictResponse
from model_service import ModelService
import uvicorn
import logging
import os
import mlflow
import redis.asyncio as aioredis
import asyncio
import hashlib, json
from starlette.status import HTTP_429_TOO_MANY_REQUESTS
from auth.api_keys import validate_api_key

import warnings
warnings.filterwarnings("ignore", category=FutureWarning)

# Uvicorn logger (recommended over print statements).
logger = logging.getLogger("uvicorn")

# Fetch MLflow Tracking URI from environment variables.
# Required so MLflow knows where the Model Registry + artifacts live.
MLFLOW_TRACKING_URI = os.getenv("MLFLOW_TRACKING_URI")

# Load Redis configuration from environment
REDIS_HOST = os.getenv("REDIS_HOST")
REDIS_PORT = int(os.getenv("REDIS_PORT"))
REDIS_DB = int(os.getenv("REDIS_DB"))
REDIS_TTL = int(os.getenv("REDIS_TTL")) 
RATE_LIMIT = int(os.getenv("RATE_LIMIT", 5))   # Max request
RATE_PERIOD = int(os.getenv("RATE_PERIOD", 10)) # seconds

# Connect to Redis
cache = aioredis.Redis(host=REDIS_HOST, port=REDIS_PORT, 
                       db=REDIS_DB, decode_responses=True,
                       max_connections=20)


# Initialize the FastAPI application with metadata (useful for docs and OpenAPI).
app = FastAPI(
    title="Telco Customer Churn Inference API",
    version="1.0.0",
    description="Serving production model from MLflow Model Registry"
)

origins = [
    "http://localhost:8501",      # Streamlit running on localhost
    "http://127.0.0.1:8501",      # Alternative localhost format
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,        # Allowed domains/origins
    allow_credentials=True,
    allow_methods=["*"],          # Allowed HTTP methods (GET, POST, etc.)
    allow_headers=["*"],          # Allowed HTTP headers
)

# Instantiate model service helper responsible for loading and running predictions.
service = ModelService()

# Startup event runs once when the server boots.
# We load the production model from the MLflow Model Registry.
@app.on_event("startup")
async def startup_event():
    # MLflow setup
    # Configure MLflow only if the environment variable exists.
    # This sets a *global* tracking URI for all MLflow operations.
    if MLFLOW_TRACKING_URI:
        mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)
        logger.info(f"MLFLOW_TRACKING_URI set to: {MLFLOW_TRACKING_URI}")

    # Redis connection
    app.state.redis = aioredis.Redis(
        host=REDIS_HOST,
        port=REDIS_PORT,
        db=REDIS_DB,
        decode_responses=True,
        max_connections=20
    )
    logger.info(f"Connected to Redis {REDIS_HOST}:{REDIS_PORT}, DB={REDIS_DB}")

    # Load model
    try:
        service.load()
        logger.info("Model loaded successfully ✅")
    except Exception as e:
        logger.error(f"Failed to load model: {e}")
        raise RuntimeError("Startup load failure. Check MLflow connectivity.")


@app.on_event("shutdown")
async def shutdown_event():
    await app.state.redis.close()
    logger.info("Redis connection closed")

# Dependency for Redis
async def get_redis():
    return app.state.redis

# Simple endpoint to verify the API is alive and a model is loaded.
@app.get("/health")
def health():
    if service.model:
        return {
            "status": "ok",
            "model_loaded": True,
            "model_name": service.model_name,
            "alias": service.alias
        }
    return {"status": "ok", "model_loaded": False}



async def rate_limiter(api_key: str = Depends(validate_api_key),
                       redis_conn: aioredis.Redis = Depends(get_redis)):
    """
    Redis-based rate limiter per API key.

    How it works:
    - Each request from a client with a given API key is counted in Redis.
    - If the number of requests exceeds RATE_LIMIT within RATE_PERIOD seconds,
      the request is blocked and the client receives an HTTP 429 response.
    """

    # Create a unique Redis key for this API key
    key = f"rate:{api_key}"  # Example: "rate:user123"

    # Atomically increment the counter in Redis
    # If the key does not exist, Redis creates it and sets the value to 1
    count = await redis_conn.incr(key)

    # If this is the first request (count = 1), set a TTL for the key
    # TTL defines the time window for rate limiting
    if count == 1:
        await redis_conn.expire(key, RATE_PERIOD)

    # If the request count exceeds the limit
    if count > RATE_LIMIT:
        # Get the remaining TTL (seconds) until the counter resets
        retry_after = await redis_conn.ttl(key)
        
        # Return HTTP 429 Too Many Requests with info about retry time
        raise HTTPException(
            status_code=HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Rate limit exceeded. Try again in {retry_after}s."
        )
# Prediction endpoint
# Accepts validated JSON based on Pydantic schema.
@app.post("/predict", response_model=PredictResponse)
async def predict(payload: PredictRequest, 
                  _: None = Depends(rate_limiter),
                  redis_conn: aioredis.Redis = Depends(get_redis)):
    try:
        # Convert Pydantic model to dictionary
        data = payload.model_dump()
        
        # Generate cache key using hash for uniqueness
        cache_key = "prediction:" + hashlib.md5(json.dumps(data, sort_keys=True).encode()).hexdigest()
        
        # Check if result exists in Redis
        cached = await redis_conn.get(cache_key)
        if cached:
            logger.info("[Cache] Returning cached result")
            # Convert the cached JSON string back into a Python dictionary
            result = json.loads(cached)

        else:
            # if there are no cached result, so we need to run inference
            # run model.predict asynchronously
            loop = asyncio.get_running_loop()
            result = await loop.run_in_executor(None, service.predict, data)
            # result = service.predict(data) # if we don't use asyncio
            # Store result in Redis asynchronously
            await redis_conn.set(cache_key, json.dumps(result), ex=REDIS_TTL)
            
            
        return {
        "prediction": result["prediction"],
        "probability": result["probability"]
        } 
    
    except Exception as e:
        logger.error(f"Inference error: {e}")
        # Return controlled HTTP error instead of internal server exception
        raise HTTPException(status_code=500, detail="Inference failure")

# Entry point for running app locally (not used inside Docker).
if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=False  # reload should remain off in production
    )
