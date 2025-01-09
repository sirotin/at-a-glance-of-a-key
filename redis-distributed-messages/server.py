from pydantic import BaseModel, Field
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from datetime import datetime, timezone, timedelta
import redis

REDIS_HOST = "localhost"
REDIS_PORT = 6379
REDIS_KEY_NAME = "messages-queue"

app = FastAPI()

redis_client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT)

@app.get("/status")
async def get_status():
    try:
        if not redis_client.ping():
            raise Exception()
        return {"status": "OK", "message": "Server is running!"}
    
    except Exception as e:
        return {"status": "Fail", "message": "Could not ping Redis!"}

class Message(BaseModel):
    message: str
    delay_sec: int = Field(..., ge=0)

@app.post("/messages")
async def post_message(msg: Message):
    try:
        # Calculate absolute time as a UNIX timestamp
        absolute_time = (datetime.now(timezone.utc) + timedelta(seconds=msg.delay_sec)).timestamp()
        
        # Insert the message into Redis ZSET
        redis_client.zadd(REDIS_KEY_NAME, {msg.message: absolute_time})
        
        return JSONResponse(
            status_code=201,
            content={"scheduled_for": absolute_time}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to add message: {e}")
