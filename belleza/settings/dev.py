from .base import *


DEBUG = True

ALLOWED_HOSTS = ["*"]


DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db3.sqlite3",
    }
}


# CELERY related settings
BROKER_URL = "amqp://localhost"
# CELERY_RESULT_BACKEND = 'amqp://'
CELERY_ACCEPT_CONTENT = ["application/json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"
CELERY_TIMEZONE = "Africa/Lagos"


AWS_ACCESS_KEY_ID = config("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = config("AWS_SECRET_ACCESS_KEY")
AWS_STORAGE_BUCKET_NAME = config("AWS_STORAGE_BUCKET_NAME")

AWS_S3_FILE_OVERWRITE = False
AWS_DEFAULT_ACL = None
AWS_S3_REGION_NAME = "us-east-1"
DEFAULT_FILE_STORAGE = "storages.backends.s3boto3.S3Boto3Storage"
