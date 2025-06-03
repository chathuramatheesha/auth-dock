from .base_config import BaseConfig
from .dev_config import DevConfig
from .prod_config import ProdConfig
from .test_config import ConfigTest


def get_config() -> ProdConfig | ConfigTest | DevConfig:
    env = BaseConfig().APP_ENV

    if env == "prod":
        return ProdConfig()
    elif env == "test":
        return ConfigTest()
    return DevConfig()
