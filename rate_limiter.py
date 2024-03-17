import time
import redis

# Connect to Redis
redis_client = redis.Redis(host='localhost', port=6379, db=0)

def rate_limit_request(client_ip, limit=5, period=60):
    current_time = time.time()
    key = f"rate_limit:{client_ip}"
    
    # Start a transaction
    with redis_client.pipeline() as pipe:
        # Remove old entries (older than the current period)
        pipe.zremrangebyscore(key, 0, current_time - period)
        # Add the new request with the current timestamp as its score
        pipe.zadd(key, {f"{current_time}": current_time})
        # Set expiration on the set to clean up if no new requests come in
        pipe.expire(key, period)
        # Count the number of requests in the last period
        request_count = pipe.zcard(key)
        pipe.execute()
    
    # Check if the request is allowed
    return request_count <= limit
