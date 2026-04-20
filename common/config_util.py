from common.path_util import CONFIG_DIR
from common.yaml_util import read_yaml


CURRENT_ENV = "uat"


def set_current_env(env_name):
    global CURRENT_ENV
    CURRENT_ENV = env_name


def get_current_env():
    return CURRENT_ENV


def get_env_config():
    env_file = CONFIG_DIR / "env" / f"{CURRENT_ENV}.yaml"
    return read_yaml(env_file)

get_env_config()


def get_base_url():
    env_config = get_env_config()
    return env_config["base_url"].rstrip("/")


def get_default_headers():
    env_config = get_env_config()
    return env_config.get("headers", {})


def get_project_config():
    return read_yaml(CONFIG_DIR / "project.yaml")



