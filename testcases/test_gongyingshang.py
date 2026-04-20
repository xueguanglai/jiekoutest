import allure
import pytest

from common.path_util import DATA_DIR
from common.response_util import validate_and_extract
from common.yaml_util import read_yaml


case_data = read_yaml(DATA_DIR / "gongyingshang" / "gongyingshang_case.yaml")


@allure.feature("供应商模块")
class TestOrder:
    @allure.story("供应商相关接口")
    @pytest.mark.parametrize("case", case_data)
    def test_order_business(self, http_client, order_login_token, case):
        if case.get("skip"):
            pytest.skip(case.get("skip_reason", "当前示例仅作为模板"))

        response = http_client.send(
            method=case["method"],
            url=case["url"],
            headers=case.get("headers", {}),
            json=case["body"],
        )
        validate_and_extract(response, case)
