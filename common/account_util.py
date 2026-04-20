from common.path_util import DATA_DIR
from common.yaml_util import read_yaml


def get_all_accounts():
    return read_yaml(DATA_DIR / "account" / "account.yaml")


def get_account_by_role(role_name):
    account_map = get_all_accounts()
    if role_name not in account_map:
        raise KeyError(f"未找到账号角色：{role_name}")
    return account_map[role_name]


def is_placeholder_account(account_data):
    phone = str(account_data.get("phone", ""))
    password = str(account_data.get("password", ""))
    return "请替换" in phone or "请替换" in password
