from datetime import datetime, timezone, timedelta
import time
import threading
import redis

# Redis connection details
REDIS_HOST = "localhost"
REDIS_PORT = 6379
SORTED_SET_KEY = "messages-queue"
STREAM_KEY = "message-stream"
CONSUMER_GROUP = "consumer-group"

# Connect to Redis
redis_client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)

def poll_messages():
    lua_script = """
    local sorted_set_key = KEYS[1]
    local stream_key = KEYS[2]
    local current_time = ARGV[1]

    -- Get messages ready for processing
    local messages = redis.call("ZRANGEBYSCORE", sorted_set_key, "-inf", current_time, "WITHSCORES")
    for i = 1, #messages, 2 do
        local message = messages[i]
        redis.call("XADD", stream_key, "*", "message", message)
        redis.call("ZREM", sorted_set_key, message)
    end
    return #messages / 2
    """
    while True:
        current_time = datetime.now(timezone.utc).timestamp()
        redis_client.eval(lua_script, 2, SORTED_SET_KEY, STREAM_KEY, current_time)
        time.sleep(1)

def process_stream():
    while True:
        messages = redis_client.xreadgroup(CONSUMER_GROUP, "consumer", {STREAM_KEY: ">"}, count=10)
        for _, entries in messages:
            for message_id, fields in entries:
                message = fields.get("message")
                print(f"{datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')}: {message}")
                redis_client.xack(STREAM_KEY, CONSUMER_GROUP, message_id)
        time.sleep(1)

def create_consumer_group():
    try:
        redis_client.xgroup_create(STREAM_KEY, CONSUMER_GROUP, id="0", mkstream=True)
        print(f"Consumer group '{CONSUMER_GROUP}' created.")
    except redis.exceptions.ResponseError as e:
        if not "BUSYGROUP" in str(e):
            raise

if __name__ == "__main__":
    print("Starting Redis message processor...")

    # Ensure the consumer group exists
    create_consumer_group()

    # Start threads
    poller = threading.Thread(target=poll_messages, daemon=True)
    processor = threading.Thread(target=process_stream, daemon=True)

    poller.start()
    processor.start()

    poller.join()
    processor.join()
