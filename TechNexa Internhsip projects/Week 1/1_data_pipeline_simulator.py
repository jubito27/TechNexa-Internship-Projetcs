import random
from collections import deque
import time
import logging

# Setup logging
logging.basicConfig(filename='pipeline.log', level=logging.INFO, format='%(asctime)s - %(message)s')

def data_stream():
    """Generator that simulates continuous incoming data."""
    while True:
        num = random.randint(1, 99)
        yield num
        time.sleep(1)

def process_data():
    window = deque(maxlen=10)
    stream = data_stream()
    
    with open('datalog.txt', 'a') as f:  # Open file for appending
    
        for _ in range(30):   # Process 30 data points, adjust as needed
            data = next(stream)
            if data > 50:
                window.append(data)
                avg = sum(window) / len(window)
                output = f"Data: {data}, Moving Average: {avg:.2f}"
                
                print(output)
                logging.info(output)
                f.write(output + '\n')

if __name__ == "__main__":
    process_data()
