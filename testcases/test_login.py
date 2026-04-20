import allure
import pytest

from api.login_api import LOGIN_BY_PASSWORD
from common.path_util import DATA_DIR
from common.response_util import validate_and_extract
from common.yaml_util import read_yaml


case_data = read_yaml(DATA_DIR / "login" / "login_case.yaml")



@allure.feature("登录模块")
class TestLogin:
    @allure.story("手机号密码登录")
    @allure.title("我是测试用例标题")
    @pytest.mark.login
    @pytest.mark.smoke
    @pytest.mark.parametrize("case", case_data)
    def test_password_login(self, http_client, case):
        with allure.step(f"执行用例: {case['title']}"):
            response = http_client.send(
                method=case["method"],
                url=LOGIN_BY_PASSWORD,
                json=case["body"],
            )

        with allure.step("断言响应并提取公共变量"):
            response_json = validate_and_extract(response, case)
            allure.attach(
                str(response_json.get("code", "")),
                name="business_code",
                attachment_type=allure.attachment_type.TEXT,
            )

    @allure.story("登录态复用")
    @pytest.mark.login
    def test_login_token_for_follow_business(self, login_token):
        assert login_token, "登录成功后没有提取到 jwtToken，请确认返回字段路径 data.jwtToken 是否正确"
        assert login_token.startswith("Bearer "), "当前登录返回的 jwtToken 应该包含 Bearer 前缀"
