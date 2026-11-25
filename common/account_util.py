from common.config_util import get_current_env
from common.path_util import DATA_DIR
from common.yaml_util import read_yaml


PLACEHOLDER_MARK = "请替换"


def get_all_accounts():
    account_file = DATA_DIR / "account" / f"{get_current_env()}.yaml"
    if not account_file.exists():
        raise FileNotFoundError(f"未找到账号文件：{account_file}")
    return read_yaml(account_file) or {}


def get_account_by_role(role_name):
    account_map = get_all_accounts()
    if role_name not in account_map:
        raise KeyError(f"未找到账号角色：{role_name}（环境：{get_current_env()}）")
    return account_map[role_name]


def is_placeholder_account(account_data):
    return PLACEHOLDER_MARK in str(account_data.get("body", ""))
