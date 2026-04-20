import allure

from api.login_api import LOGIN_BY_PASSWORD, build_password_login_body
from common.response_util import validate_and_extract


def login_by_password(
    http_client,
    phone,
    password,
    area_code="86",
    slider_code="",
    sign_key="f4c9f2e1256ac58852ff5d9ceea72b7a",
    login_type=2,
):
    body = build_password_login_body(
        phone=phone,
        password=password,
        area_code=area_code,
        slider_code=slider_code,
        sign_key=sign_key,
        login_type=login_type,
    )
    case = {
        "title": "登录获取 token",
        "method": "post",
        "url": LOGIN_BY_PASSWORD,
        "body": body,
        "expected_status_code": 200,
        "expected_business_codes": ["200"],
        "expected_keys": ["code", "data", "data.jwtToken", "data.memberId"],
        "extract": {
            "jwtToken": "data.jwtToken",
            "memberId": "data.memberId",
            "phone": "data.phone",
        },
    }

    with allure.step("执行登录，获取后续业务需要的 token"):
        response = http_client.send(
            method=case["method"],
            url=case["url"],
            json=case["body"],
        )
    return validate_and_extract(response, case)
