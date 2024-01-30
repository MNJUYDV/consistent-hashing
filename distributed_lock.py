import redis
import time
import random

class Redlock:
    def __init__(self, redis_nodes, retry_count=3, retry_delay=0.2):
        self.redis_nodes = redis_nodes
        self.retry_count = retry_count
        self.retry_delay = retry_delay

    def acquire_lock(self, resource, ttl):
        for _ in range(self.retry_count):
            acquired_nodes = 0
            lock_value = str(time.time() + ttl + 1)  # Set lock expiration slightly longer

            for node in self.redis_nodes:
                redis_client = redis.StrictRedis(host=node['host'], port=node['port'], db=node['db'])

                # Attempt to acquire the lock on each Redis node
                if redis_client.set(resource, lock_value, nx=True, ex=ttl):
                    acquired_nodes += 1

            # If the lock was acquired from the majority of nodes, return success
            if acquired_nodes > len(self.redis_nodes) / 2:
                return True

            # Sleep and retry after a random delay
            time.sleep(random.uniform(0, self.retry_delay))

        return False

    def release_lock(self, resource):
        for node in self.redis_nodes:
            redis_client = redis.StrictRedis(host=node['host'], port=node['port'], db=node['db'])
            redis_client.delete(resource)

# Example usage:
if __name__ == '__main__':
    redis_nodes = [
        {'host': 'localhost', 'port': 6379, 'db': 0},
        {'host': 'localhost', 'port': 6380, 'db': 0},
        {'host': 'localhost', 'port': 6381, 'db': 0}
    ]

    redlock = Redlock(redis_nodes)

    resource = 'my_lock_resource'
    ttl = 10  # Lock expiration time in seconds

    if redlock.acquire_lock(resource, ttl):
        try:
            # Critical section - perform exclusive operation
            print("Acquired lock, performing critical section")
            time.sleep(5)  # Simulate some work
        finally:
            redlock.release_lock(resource)
    else:
        print("Failed to acquire lock")
