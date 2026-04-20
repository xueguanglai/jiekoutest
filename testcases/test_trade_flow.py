import allure
import pytest

from common.context_util import test_context


@allure.feature("交易主流程")
class TestTradeFlow:
    @allure.story("登录-商品-购物车-订单")
    @pytest.mark.skip(reason="当前为流程模板，需要接入真实接口后再执行")
    def test_trade_flow_demo(self):
        """
        这个文件是给团队看的流程模板。
        实际落地时，建议按下面顺序组织用例：
        1. 登录后提取 token
        2. 查询商品后提取 skuId
        3. 加入购物车
        4. 创建订单后提取 orderId
        5. 查询订单详情
        """
        assert test_context.all() == {}
