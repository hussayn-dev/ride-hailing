import os

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.0/howto/static-files/

APP_NAME = os.getenv("APP_NAME")
STATIC_LOCATION = f"{APP_NAME}/static"
MEDIA_LOCATION = f"{APP_NAME}/media"
AWS_DEFAULT_ACL = "public-read"
AWS_QUERYSTRING_AUTH = False
AWS_S3_SIGNATURE_VERSION = "s3v4"
AWS_S3_ADDRESSING_STYLE = "virtual"
AWS_ACCESS_KEY_ID = ""
AWS_SECRET_ACCESS_KEY = ""
AWS_STORAGE_BUCKET_NAME = ""
AWS_S3_REGION_NAME = ""
AWS_S3_ENDPOINT_URL = f"https://{AWS_S3_REGION_NAME}.digitaloceanspaces.com"
AWS_S3_CUSTOM_DOMAIN = ""
AWS_S3_OBJECT_PARAMETERS = {"CacheControl": "max-age=86400"}
AWS_LOCATION = STATIC_LOCATION
STATIC_URL = f"https://{AWS_S3_ENDPOINT_URL}/{AWS_LOCATION}/"
# public media settings
PUBLIC_MEDIA_LOCATION = MEDIA_LOCATION
MEDIA_URL = f"https://{AWS_S3_ENDPOINT_URL}/{PUBLIC_MEDIA_LOCATION}/"
DEFAULT_FILE_STORAGE = "storages.backends.s3boto3.S3Boto3Storage"
STATICFILES_STORAGE = "storages.backends.s3boto3.S3StaticStorage"

IMPORT_EXPORT_TMP_STORAGE_CLASS = "import_export.tmp_storages.MediaStorage"

STORAGES = {
    "default": {
        "BACKEND": "storages.backends.s3.S3Storage",
        "OPTIONS": {
            "access_key": AWS_ACCESS_KEY_ID,
            "secret_key": AWS_SECRET_ACCESS_KEY,
            "bucket_name": AWS_STORAGE_BUCKET_NAME,
            "region_name": AWS_S3_REGION_NAME,
            "endpoint_url": AWS_S3_ENDPOINT_URL,
            "custom_domain": AWS_S3_CUSTOM_DOMAIN,
            "location": AWS_LOCATION,
            "default_acl": AWS_DEFAULT_ACL,
            "object_parameters": {
                "CacheControl": "max-age=86400",
            },
        },
    },
    "staticfiles": {"BACKEND": "storages.backends.s3.S3Storage"},
    "import_export": {
        "BACKEND": "storages.backends.s3.S3Storage",
        "OPTIONS": {
            "bucket_name": AWS_STORAGE_BUCKET_NAME,
            "region_name": AWS_S3_REGION_NAME,
            "access_key": AWS_ACCESS_KEY_ID,
            "secret_key": AWS_SECRET_ACCESS_KEY,
        },
    },
}
