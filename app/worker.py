from taskiq.events import TaskiqEvents
from taskiq.state import TaskiqState
from taskiq_redis import RedisStreamBroker, RedisAsyncResultBackend

from app.settings import settings
from app.service.minio import ensure_buckets

redis_url = settings.BROKER_URL
broker = RedisStreamBroker(
    url=redis_url
).with_result_backend(RedisAsyncResultBackend(redis_url, result_ex_time=1000, keep_results=False))


@broker.on_event(TaskiqEvents.WORKER_STARTUP)
async def startup(state: TaskiqState) -> None:
    ensure_buckets()