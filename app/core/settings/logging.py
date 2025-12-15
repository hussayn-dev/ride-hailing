LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "json": {
            "format": '{"timestamp": "%(asctime)s", "level": "%(levelname)s", "message": "%(message)s", '
                      '"module": "%(module)s", "function": "%(funcName)s", "line": %(lineno)d}'
        },
        "colored": {
            "()": "colorlog.ColoredFormatter",
            "format": "%(asctime)s:%(log_color)s%(levelname)s:%(name)s:%(message)s ------------",
            "datefmt": "%Y-%m-%d %H:%M:%S",
            "log_colors": {
                "DEBUG": "cyan",
                "INFO": "green",
                "WARNING": "yellow",
                "ERROR": "red",
                "CRITICAL": "bold_red",
            },
        },
        "verbose": {
            "format": (
                "\n--- %(levelname)s ---\n"
                "Timestamp: %(asctime)s\n"
                "Message: %(message)s\n"
                "Location: %(pathname)s:%(lineno)d in %(funcName)s\n"
                "-------------------------------------------------\n"
            ),
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
    },
    "handlers": {
        "console": {
            "level": "INFO",
            "class": "logging.StreamHandler",
            "formatter": "colored",
        },
    },
    "loggers": {
        # Catch all Django-related logs here
        "django": {
            "handlers": ["console"],
            "level": "DEBUG",
            "propagate": False,
        },
    },
    # Root logger for all other logs
    "root": {
        "handlers": ["console", ],
        "level": "INFO",
    },
}

DRF_API_LOGGER_EXCLUDE_KEYS = [
    "tx_pin",
    "bvn",
    "nin",
    "X-KMS-KEY",
    "Authorization",
    "transaction_pin",
]
