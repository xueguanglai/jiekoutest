from urllib.parse import quote

from common.config_util import get_login_config


_active_token = None


def set_token(token):
    global _active_token
    _active_token = token


def clear_token():
    set_token(None)


def get_token():
    return _active_token


def build_auth_headers():
    if not _active_token:
        return {}
    login_config = get_login_config()
    token = str(_active_token)
    if login_config.get("token_urlencode"):
        token = quote(token, safe="")
    header_name = login_config.get("token_header", "Authorization")
    token_format = login_config.get("token_format") or "{token}"
    return {header_name: token_format.replace("{token}", token)}
