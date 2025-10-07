from taskiq_redis import RedisStreamBroker, RedisAsyncResultBackend

from app.settings import settings

redis_url = settings.BROKER_URL
broker = RedisStreamBroker(
    url=redis_url
).with_result_backend(RedisAsyncResultBackend(redis_url, result_ex_time=1000, keep_results=False))
