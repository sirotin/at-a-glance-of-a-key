**Run Redis server within Docker**
```
docker pull redis
docker run -d --name redis-server -p 6379:6379 redis
```

**Create Virtual Environment**
```
python3 -m venv myenv
source myenv/bin/activate
pip3 install -r requirements.txt
```

**Run the server**
```
source myenv/bin/activate
uvicorn server:app --reload
```

**Run the Consumer**
For the simple consumer, just run the "simple-consumer.py" script within myenv.
For the streams consumer, run both "streams-consumer.py" script within myenv.

**Generating Load**
Run the producer.py script or call the API endpoint:
```
curl -X POST http://localhost:8000/messages -H "Content-Type: application/json" \
-d '{"message": "Ohh, hello there.", "delay_sec": 5}'
```
