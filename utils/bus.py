import threading
import queue
import time



"""
This class emulates a bus network. When a subscriber sends a message, all other
subscribers receive the message. Each one has its own queue of received messages.
"""
class Bus:
    def __init__(self):
        # Dictionary that maps IDs from subscribers to their queues
        self.subscribers = {}
        self.lock = threading.Lock()

    def register(self, subscriber_id):
        """
        Registers a new subscriber and returns its queue.
        """
        with self.lock:
            q = queue.Queue()
            self.subscribers[subscriber_id] = q
            return q

    def unregister(self, subscriber_id):
        """
        Removes a subscriber.
        """
        with self.lock:
            if subscriber_id in self.subscribers:
                del self.subscribers[subscriber_id]

    def send_message(self, message):
        """
        Publishes a message to all subscribers.
        Each subscriber reveives its own copy of the message.
        """
        with self.lock:
            for q in self.subscribers.values():
                q.put(message)

    def wait_for_new_message(self, subscriber_id, timeout=None):
        """
        Allows a subscriber to wait for a new message.
        Returns True if a message is available, or False if timeout occurs.
        """
        q = self.subscribers.get(subscriber_id)
        t0 = time.time()
        while q.empty():
            if timeout is not None and time.time() - t0 > timeout:
                return False
            time.sleep(0.01)
        return True

    def get_messages(self, subscriber_id):
        """
        Returns all messages available in the subscriber queue.
        """
        messages = []
        q = self.subscribers.get(subscriber_id)
        if q:
            while True:
                try:
                    msg = q.get_nowait()
                    messages.append(msg)
                except queue.Empty:
                    break
        return messages
