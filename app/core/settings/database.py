import os

DATABASES = {
    "default": {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        "NAME": os.environ.get("POSTGRES_DB"),
        "USER": os.environ.get("POSTGRES_USER"),
        "PASSWORD": os.environ.get("POSTGRES_PASSWORD"),
        "HOST": os.environ.get("POSTGRES_HOST"),
        "PORT": os.environ.get("POSTGRES_PORT"),
    },
}


# DATABASES = {
#     'default': {
#         **dj_database_url.config(default=os.environ.get('DATABASE_URL')),
#         'ENGINE': 'django.contrib.gis.db.backends.postgis',
#     }
# }
