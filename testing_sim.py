import requests
import random
import time


BACKEND_URL = "https://met-rbic.onrender.com/metrics"

while True:
    data = {
        "scanned": random.randint(1000, 3000),
        "anomalies": random.randint(10, 60),
        "fps": round(10 + random.random() * 10, 2),
        "epochs": [1, 2, 3, 4, 5],
        "precision": [round(0.6 + random.random() * 0.3, 2) for _ in range(5)],
        "recall":    [round(0.5 + random.random() * 0.3, 2) for _ in range(5)],
        "f1":        [round(0.55 + random.random() * 0.3, 2) for _ in range(5)],
    }

    response = requests.post(BACKEND_URL, json=data)
    print("Sent:", data)
    print("Response:", response.json())

    time.sleep(3)
