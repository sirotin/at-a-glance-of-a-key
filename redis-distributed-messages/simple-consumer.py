from datetime import datetime, timezone
import time
import redis

# Redis connection details
REDIS_HOST = "localhost"
REDIS_PORT = 6379
REDIS_KEY_NAME = "messages-queue"

# Connect to Redis
redis_client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)

def poll_messages():
    while True:
        current_time = datetime.now(timezone.utc).timestamp()

        messages = redis_client.zrangebyscore(REDIS_KEY_NAME, "-inf", current_time, withscores=True)

        if messages:
            for message, timestamp in messages:
                print(f"{datetime.fromtimestamp(timestamp, timezone.utc).strftime('%Y-%m-%d %H:%M:%S')}: {message}")
                redis_client.zrem(REDIS_KEY_NAME, message)

        time.sleep(1)

if __name__ == "__main__":
    print("Polling Redis for messages...")
    poll_messages()
