import threading
import queue
import time
import random

def producer(q, num_items):
    for i in range(num_items):
        item = f"item-{i}"
        time.sleep(random.uniform(0.05, 0.2))
        q.put(item)
        print(f"Produced: {item}")
    q.put(None)  # sentinel to signal done

def consumer(q):
    while True:
        item = q.get()
        if item is None:
            break
        time.sleep(random.uniform(0.1, 0.3))
        print(f"Consumed: {item}")
        q.task_done()


if __name__ == "__main__":
    q = queue.Queue()
    prod_thread = threading.Thread(target=producer, args=(q, 5))
    cons_thread = threading.Thread(target=consumer, args=(q,))

    prod_thread.start()
    cons_thread.start()
    prod_thread.join()
    cons_thread.join()
    print("Done!")
