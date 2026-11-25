from common.path_util import CONFIG_DIR
from common.yaml_util import read_yaml


_current_env = None


def get_project_config():
    return read_yaml(CONFIG_DIR / "project.yaml")


def set_current_env(env_name):
    global _current_env
    _current_env = env_name


def get_current_env():
    return _current_env or get_project_config().get("default_env", "uat")


def get_env_config():
    env_file = CONFIG_DIR / "env" / f"{get_current_env()}.yaml"
    if not env_file.exists():
        raise FileNotFoundError(f"未找到环境配置文件：{env_file}")
    return read_yaml(env_file)


def get_base_url():
    return get_env_config()["base_url"].rstrip("/")


def get_default_headers():
    return get_env_config().get("headers") or {}


def get_login_config():
    return get_env_config().get("login") or {}
