import time
from app import app
import json

app.config['TESTING'] = True
client = app.test_client()

start = time.time()
response = client.get('/api/chart/589fabff-bf49-405a-9372-6d9566bf6955')
end = time.time()
print(f"Time taken: {end - start:.2f} seconds")
