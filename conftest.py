import pytest
from pathlib import Path
from datetime import datetime

from common.config_util import set_current_env
from common.account_util import get_account_by_role, is_placeholder_account
from common.context_util import test_context
from common.login_service import login_by_password
from common.notify_util import send_dingtalk_notification
from common.report_util import (
    add_test_case_result,
    build_custom_html_report,
    clear_current_test,
    clear_test_case_results,
    get_test_case_results,
    pop_api_records,
    set_current_test,
)
from common.request_util import HttpClient
from common.yaml_util import read_yaml
from common.path_util import DATA_DIR


def pytest_addoption(parser):
    parser.addoption(
        "--env",
        action="store",
        default="uat",
        help="运行环境，例如：uat",
    )


def pytest_configure(config):
    report_dir = Path(__file__).resolve().parent / "reports"
    report_dir.mkdir(exist_ok=True)
    module_name = "all"
    if config.args:
        module_name = Path(str(config.args[0])).stem or "all"
    report_name = f"{datetime.now().strftime('%Y-%m%d-%H:%M')}{module_name}测试报告.html"
    config._custom_html_report_path = report_dir / report_name
    config._custom_html_report_title = report_name


def pytest_sessionstart(session):
    clear_test_case_results()


@pytest.fixture(autouse=True)
def init_current_test(request):
    set_current_test(request.node.nodeid)
    yield
    clear_current_test()


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()
    case = getattr(getattr(item, "callspec", None), "params", {}).get("case", {})
    case_title = case.get("title") if isinstance(case, dict) else item.name

    if report.when == "setup" and report.failed:
        add_test_case_result(
            {
                "title": case_title,
                "nodeid": item.nodeid,
                "status": "error",
                "duration": round(report.duration, 3),
                "error_message": str(report.longrepr),
                "api_records": pop_api_records(item.nodeid),
            }
        )
        return

    if report.when != "call":
        return

    status = "passed"
    if report.failed:
        status = "failed"
    elif report.skipped:
        status = "skipped"

    add_test_case_result(
        {
            "title": case_title,
            "nodeid": item.nodeid,
            "status": status,
            "duration": round(report.duration, 3),
            "error_message": "" if report.passed else str(report.longrepr),
            "api_records": pop_api_records(item.nodeid),
        }
    )


def pytest_sessionfinish(session, exitstatus):
    report_path = getattr(session.config, "_custom_html_report_path", None)
    report_title = getattr(session.config, "_custom_html_report_title", "自动化测试报告")
    if not report_path:
        return

    html_content = build_custom_html_report(report_title, get_test_case_results())
    report_path.write_text(html_content, encoding="utf-8")
    send_dingtalk_notification()

@pytest.fixture(scope="session", autouse=True)
def init_test_env(request):
    env_name = request.config.getoption("--env")
    set_current_env(env_name)


@pytest.fixture(scope="session")
def http_client():
    client = HttpClient()
    yield client
    client.close()


@pytest.fixture(scope="session")
def login_data():
    return get_account_by_role("order_user")


@pytest.fixture(scope="session")
def account_data_map():
    return {
        "order_user": get_account_by_role("order_user"),
        "product_user": get_account_by_role("product_user"),
        "refund_user": get_account_by_role("refund_user"),
    }


@pytest.fixture(scope="session")
def role_login(http_client):
    def _login(role_name):
        account_data = get_account_by_role(role_name)
        if is_placeholder_account(account_data):
            pytest.skip(f"{role_name} 账号还是占位数据，请先在 data/account/account.yaml 中替换")

        test_context.clear()
        login_by_password(
            http_client=http_client,
            phone=account_data["phone"],
            password=account_data["password"],
            area_code=account_data["areaCode"],
            slider_code=account_data["sliderCode"],
            sign_key=account_data["signKey"],
            login_type=account_data["loginType"],
        )
        return test_context.get("jwtToken")

    return _login


@pytest.fixture(scope="session")
def login_token(http_client, login_data):
    if is_placeholder_account(login_data):
        pytest.skip("order_user 账号还是占位数据，请先在 data/account/account.yaml 中替换")
    test_context.clear()
    login_by_password(
        http_client=http_client,
        phone=login_data["phone"],
        password=login_data["password"],
        area_code=login_data["areaCode"],
        slider_code=login_data["sliderCode"],
        sign_key=login_data["signKey"],
        login_type=login_data["loginType"],
    )
    return test_context.get("jwtToken")


@pytest.fixture(scope="session")
def order_login_data():
    return get_account_by_role("order_user")


@pytest.fixture(scope="session")
def product_login_data():
    return get_account_by_role("product_user")


@pytest.fixture(scope="session")
def refund_login_data():
    return get_account_by_role("refund_user")


@pytest.fixture(scope="session")
def order_login_token(role_login):
    return role_login("order_user")


@pytest.fixture(scope="session")
def product_login_token(role_login):
    return role_login("product_user")


@pytest.fixture(scope="session")
def refund_login_token(role_login):
    return role_login("refund_user")



@pytest.fixture(scope="session")
def gongyinglian_login_token(role_login):
    return role_login("gongyinglian_user")



