import allure
import pytest

from common.auth_util import build_auth_headers
from common.case_util import load_cases


@allure.feature("登录模块")
class TestLogin:
    @allure.story("账号密码登录")
    @allure.title("登录成功并生成后续业务使用的登录态")
    @pytest.mark.smoke
    def test_login_success(self, role_login):
        token = role_login("manage_user")
        assert token.startswith("Bearer "), f"jwtToken 应以 Bearer 开头，实际：{token[:20]}"
        cookie = build_auth_headers()["Cookie"]
        assert "eh_uatJwtToken=Bearer%20" in cookie, "Cookie 中没有正确拼入 eh_uatJwtToken"

    @allure.story("账号密码登录_异常场景")
    @pytest.mark.parametrize("case", load_cases("login"))
    def test_login_invalid(self, run_case, case):
        run_case(case)
