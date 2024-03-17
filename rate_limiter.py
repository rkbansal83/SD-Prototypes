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


### Example Scenario

Let's assume the following:
- A client with IP `192.168.1.1` makes requests to an endpoint.
- The rate limit is set to 5 requests per 60 seconds.

1. **First Request**: The client makes their first request.
    - The current timestamp is `1609459200` (just an example timestamp).
    - The sorted set key `rate_limit:192.168.1.1` is checked. Since this is the first request, it's added to the set.
    - The count of requests in the set is now 1, which is less than the limit of 5. The request is allowed.

2. **Subsequent Requests**: The client makes four more requests within the next 60 seconds.
    - Each request adds a new timestamp to the sorted set and checks the count.
    - As long as the count doesn’t exceed 5, the requests are allowed.

3. **Sixth Request**: If the client makes a sixth request within the same 60-second window:
    - The count of timestamps in the set would be 6, which exceeds the limit.
    - The function returns `False`, indicating the rate limit has been exceeded, and the request should be denied.
