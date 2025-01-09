import asyncio
import aiohttp
import random
import string
import time
from aiohttp import ClientSession

# Configurations
API_URL = "http://localhost:8000/messages"
SEND_RATE = 10  # Number of messages to send per second
DURATION = 30  # Duration to send messages (seconds)
TOTAL_REQUESTS = SEND_RATE * DURATION

# Function to generate random messages
def generate_random_message(length=10):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

# Function to perform a POST request to the API
async def post_message(session: ClientSession, message: str, delay_sec: int):
    payload = {
        "message": message,
        "delay_sec": delay_sec
    }
    try:
        async with session.post(API_URL, json=payload) as response:
            if response.status == 201:
                pass
            else:
                print(f"Failed to post message: {message} (Status: {response.status})")
    except Exception as e:
        print(f"Error posting message: {message} ({str(e)})")

# Function to run concurrent requests at a fixed rate
async def send_messages():
    async with aiohttp.ClientSession() as session:
        for _ in range(TOTAL_REQUESTS):
            message = generate_random_message()
            delay_sec = random.randint(1, 15)
            await post_message(session, message, delay_sec)
            await asyncio.sleep(1 / SEND_RATE)

# Main entry point with timeout handling
def main():
    start_time = time.time()
    try:
        asyncio.run(send_messages())
    except asyncio.TimeoutError:
        print("Request timed out")
    end_time = time.time()
    print(f"Total time: {end_time - start_time:.2f} seconds")

if __name__ == "__main__":
    main()