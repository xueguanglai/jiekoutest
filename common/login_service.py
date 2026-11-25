import allure

from common.account_util import get_account_by_role
from common.auth_util import clear_token
from common.config_util import get_current_env, get_login_config
from common.extract_util import get_value_by_path
from common.response_util import validate_response


def login(http_client, role_name):
    """用 data/account/<env>.yaml 中该角色的 body 调登录接口，返回 token。"""
    login_config = get_login_config()
    if not login_config.get("url"):
        raise ValueError(f"config/env/{get_current_env()}.yaml 中没有配置 login.url")

    account = get_account_by_role(role_name)
    clear_token()
    with allure.step(f"登录角色：{role_name}"):
        response = http_client.send(
            method=login_config.get("method", "post"),
            url=login_config["url"],
            json=account["body"],
        )
    response_json = validate_response(
        response,
        {
            "expected_status_code": login_config.get("expected_status_code", 200),
            "expected_business_codes": login_config.get("success_codes"),
        },
    )

    token_path = login_config.get("token_path", "data.token")
    try:
        return get_value_by_path(response_json, token_path)
    except KeyError as exc:
        raise AssertionError(
            f"登录成功但未取到 token，路径：{token_path}，实际响应：{response_json}"
        ) from exc
