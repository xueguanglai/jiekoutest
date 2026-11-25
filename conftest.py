from datetime import datetime
from pathlib import Path

import pytest

from common.account_util import get_account_by_role, is_placeholder_account
from common.auth_util import clear_token, set_token
from common.case_util import execute_case
from common.config_util import get_current_env, get_project_config, set_current_env
from common.context_util import test_context
from common.login_service import login
from common.notify_util import send_dingtalk_notification
from common.path_util import REPORT_DIR
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


def pytest_addoption(parser):
    parser.addoption(
        "--env",
        action="store",
        default=None,
        help="运行环境，对应 config/env/<env>.yaml；不传则使用 project.yaml 的 default_env",
    )


def pytest_configure(config):
    # 用例数据在收集阶段就会读取，所以环境必须在这里确定，不能放到 fixture 里。
    set_current_env(config.getoption("--env") or get_current_env())

    module_name = "all"
    if config.args:
        module_name = Path(str(config.args[0]).split("::")[0]).stem or "all"
    now = datetime.now()
    # 文件名只用英文数字，保证能直接拼进报告链接。
    config._custom_html_report_path = (
        REPORT_DIR / f"{now.strftime('%Y%m%d-%H%M%S')}_{module_name}.html"
    )
    config._custom_html_report_title = (
        f"{now.strftime('%Y-%m-%d %H:%M')} {module_name} 测试报告"
    )


def pytest_sessionstart(session):
    clear_test_case_results()


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()
    case = getattr(getattr(item, "callspec", None), "params", {}).get("case", {})
    case_title = case.get("title") if isinstance(case, dict) else item.name

    if report.when == "setup" and report.failed:
        status = "error"
    elif report.when == "setup" and report.skipped:
        status = "skipped"
    elif report.when != "call":
        return
    elif report.failed:
        status = "failed"
    elif report.skipped:
        status = "skipped"
    else:
        status = "passed"

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


def remove_old_reports(keep_count):
    """只保留最新的 keep_count 份 HTML 报告，避免 reports/ 无限增长。"""
    reports = sorted(
        REPORT_DIR.glob("*.html"), key=lambda path: path.stat().st_mtime, reverse=True
    )
    for old_report in reports[max(int(keep_count), 1):]:
        old_report.unlink()


def pytest_sessionfinish(session, exitstatus):
    results = get_test_case_results()
    if not results:
        return

    REPORT_DIR.mkdir(exist_ok=True)
    report_path = session.config._custom_html_report_path
    report_path.write_text(
        build_custom_html_report(session.config._custom_html_report_title, results),
        encoding="utf-8",
    )
    remove_old_reports(get_project_config().get("report_keep_count", 3))
    send_dingtalk_notification(report_path)


@pytest.fixture(autouse=True)
def init_current_test(request):
    set_current_test(request.node.nodeid)
    yield
    clear_current_test()


@pytest.fixture(scope="module", autouse=True)
def reset_context():
    """每个测试文件一份干净的上下文和登录态，避免模块之间变量串用。"""
    test_context.clear()
    clear_token()
    yield


@pytest.fixture(scope="session")
def http_client():
    client = HttpClient()
    yield client
    client.close()


@pytest.fixture(scope="session")
def role_login(http_client):
    """按角色登录并切换当前 token；同一角色整个会话只登录一次。"""
    tokens = {}

    def _login(role_name):
        if role_name not in tokens:
            if is_placeholder_account(get_account_by_role(role_name)):
                pytest.skip(
                    f"{role_name} 账号还是占位数据，请先在 data/account/{get_current_env()}.yaml 中替换"
                )
            tokens[role_name] = login(http_client, role_name)
        set_token(tokens[role_name])
        return tokens[role_name]

    return _login


@pytest.fixture
def run_case(http_client, role_login):
    """执行一条 YAML 用例：登录(可选) -> 发请求 -> 断言 -> 提取变量。"""

    def _run(case, role=None):
        return execute_case(http_client, case, login=role_login, default_role=role)

    return _run
