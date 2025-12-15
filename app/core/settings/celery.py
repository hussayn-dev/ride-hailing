import os

from celery.schedules import crontab
from kombu import Exchange, Queue

APP_NAME = os.getenv("APP_NAME", "django-api")
REDIS_URL = os.getenv("REDIS_URL", "localhost:6379")

CELERY_RESULT_BACKEND = REDIS_URL
CELERY_BROKER_URL = os.environ.get("CELERY_BROKER_URL")
CELERY_SEND_TASK_SENT_EVENT = True
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"
CELERY_ACCEPT_CONTENT = ["json"]
CELERY_BROKER_CONNECTION_RETRY_ON_STARTUP = True
CELERY_TASK_RESULT_EXPIRES = 18000

CELERY_QUEUES = (Queue("reversal_queue", Exchange("reversal"), routing_key="reversal"),)
CELERY_ROUTES = {
    "transaction.tasks.reverse_transaction_task": {"queue": "reversal_queue"},
}

CELERY_TASK_DEFAULT_QUEUE = "default"

FLOWER_BASIC_AUTH = os.environ.get("FLOWER_BASIC_AUTH")
# Assumes that the username is swift or simple have the url as redis://swift:jetSwift@localhost:6379/0
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": REDIS_URL,
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        },
        "KEY_PREFIX": APP_NAME,
    }
}

SESSION_ENGINE = "django.contrib.sessions.backends.cache"
SESSION_CACHE_ALIAS = "default"

CACHE_TTL = 60 * 1
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [REDIS_URL],
        },
        # 'ROUTING': 'core'
    },
}

CELERY_BEAT_SCHEDULE = {
    "run_terminal_auto_debit": {
        "task": "wallet.tasks.run_auto_debit_process",
        "schedule": crontab(minute="0", hour="0", day_of_month="*"),
    }
}
