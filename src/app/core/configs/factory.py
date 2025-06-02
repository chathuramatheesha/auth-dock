from .base_config import BaseConfig
from .dev_config import DevConfig
from .prod_config import ProdConfig
from .test_config import TestConfig


def get_config() -> ProdConfig | TestConfig | DevConfig:
    env = BaseConfig().APP_ENV

    if env == "prod":
        return ProdConfig()
    elif env == "test":
        return TestConfig()
    return DevConfig()
