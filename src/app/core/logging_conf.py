import logging
from logging.config import dictConfig

from app.core.configs import config
from app.core.configs.dev_config import DevConfig


def obfuscated(email: str, obfuscated_length: int) -> str:
    characters = email[0:obfuscated_length]
    first, last = email.split("@")
    obfuscated_email = f"{characters}{'*' * (len(first) - obfuscated_length)}@{last}"
    return obfuscated_email


# Custom Filter
class EmailObfuscationFilter(logging.Filter):
    def __init__(self, name: str = "", obfuscated_length: int = 2) -> None:
        super().__init__(name)
        self.obfuscated_length = obfuscated_length

    def filter(self, record: logging.LogRecord) -> bool:
        if "email" in record.__dict__:
            record.email = obfuscated(record.email, self.obfuscated_length)
        return True


async def configure_logging() -> None:
    dictConfig(
        {
            "version": 1,
            "disable_existing_loggers": False,
            "filters": {
                "correlation_id": {
                    # filter = asgi_correlation_id.CorrelationFilter(uuid_length=8, default_value='-')
                    "()": "asgi_correlation_id.CorrelationIdFilter",
                    "uuid_length": 8 if isinstance(config, DevConfig) else 32,
                    "default_value": "-",
                },
                "email_obfuscation": {
                    "()": EmailObfuscationFilter,
                    "obfuscated_length": 2 if isinstance(config, DevConfig) else 0,
                },
            },
            "formatters": {
                "console": {
                    "class": "logging.Formatter",
                    "datefmt": "%Y-%m-%dT%H:%M:%S",
                    "format": "(%(correlation_id)s) %(name)s:%(lineno)d - %(message)s",
                },
                "file": {
                    # "class": "logging.Formatter",  # Normal Formatter
                    "class": "pythonjsonlogger.jsonlogger.JsonFormatter",  # Json Formatter
                    "datefmt": "%Y-%m-%dT%H:%M:%S",
                    # "format": "%(asctime)s.%(msecs)03dZ | %(levelname)-8s | [%(correlation_id)s] %(name)s:%(lineno)d - %(message)s",  # For normal format
                    "format": "%(asctime)s %(msecs)03d  %(levelname)-8s %(correlation_id)s %(name)s %(lineno)d %(message)s",  # Json formatter doesn't care about decor only care about variables
                },
            },
            "handlers": {
                "default": {
                    # "class": "logging.StreamHandler", # Default logger
                    "class": "rich.logging.RichHandler",  # rich logger (rich library)
                    "level": "DEBUG",
                    "formatter": "console",
                    "filters": ["correlation_id", "email_obfuscation"],
                },
                "rotating_file": {
                    "class": "logging.handlers.RotatingFileHandler",
                    "level": "DEBUG",
                    "formatter": "file",
                    "filename": "auth-dock.log",
                    "maxBytes": 1024 * 1024,  # 1 MB
                    "backupCount": 2,  # only two log files keeping
                    "encoding": "utf8",
                    "filters": ["correlation_id", "email_obfuscation"],
                },
                # "logtail": {
                #     "class": "logtail.LogtailHandler",
                #     "level": "DEBUG",
                #     "formatter": "console",
                #     "filters": ["correlation_id", "email_obfuscation"],
                #     "source_token": config.LOGTAIL_API_KEY,
                # },
            },
            "loggers": {
                "uvicorn": {
                    "handlers": ["default", "rotating_file"],
                    "level": "INFO",
                },
                "app": {
                    "handlers": ["default", "rotating_file"],  # "logtail"],
                    "level": "DEBUG" if isinstance(config, DevConfig) else "INFO",
                    "propagate": False,  # Doesn't send loggers to parent
                },
                "databases": {"handlers": ["default"], "level": "WARNING"},
                "aiosqlite": {"handlers": ["default"], "level": "WARNING"},
            },
        }
    )
