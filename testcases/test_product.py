import allure
import pytest

from common.path_util import DATA_DIR
from common.response_util import validate_and_extract
from common.yaml_util import read_yaml


case_data = read_yaml(DATA_DIR / "product" / "product_case.yaml")


@allure.feature("商品模块")
class TestProduct:
    @allure.story("商品列表")
    @pytest.mark.parametrize("case", case_data)
    def test_product_list(self, http_client, product_login_token, case):
        if case.get("skip"):
            pytest.skip(case.get("skip_reason", "当前示例仅作为模板"))

        response = http_client.send(
            method=case["method"],
            url=case["url"],
            json=case["body"],
        )
        validate_and_extract(response, case)
