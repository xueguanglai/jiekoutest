import os
from pathlib import Path
from urllib.parse import quote

import requests

from common.config_util import get_current_env, get_project_config
from common.logger_util import get_logger
from common.report_util import get_test_case_results


MAX_FAILED_CASES = 10


def get_report_base_url():
    """报告访问地址前缀：环境变量 REPORT_BASE_URL 优先，其次 project.yaml 的 report_base_url。"""
    base_url = os.environ.get("REPORT_BASE_URL") or get_project_config().get("report_base_url") or ""
    return base_url.strip().rstrip("/")


def build_dingtalk_markdown(report_path=None):
    project_config = get_project_config()
    keyword = project_config.get("dingtalk_keyword", "自动化告警")
    image_url = project_config.get("dingtalk_image_url", "")

    cases = get_test_case_results()
    counts = {status: 0 for status in ("passed", "failed", "error", "skipped")}
    for case in cases:
        counts[case["status"]] = counts.get(case["status"], 0) + 1
    failed_cases = [case for case in cases if case["status"] in {"failed", "error"}]
    if not failed_cases and not project_config.get("dingtalk_notify_on_success", False):
        return None

    result_text = (
        f"<font color=\"#dc2626\">有 {len(failed_cases)} 条未通过</font>"
        if failed_cases
        else "<font color=\"#16a34a\">全部通过</font>"
    )
    total_duration = round(sum(case.get("duration", 0) for case in cases), 2)
    lines = [
        f"### {keyword}｜接口自动化{'告警' if failed_cases else '报告'}",
        "",
        f"- 项目：{project_config.get('project_name', '接口自动化测试')}",
        f"- 环境：{get_current_env()}",
        f"- 结果：{result_text}",
        f"- 总用例：{len(cases)}",
        f"- 通过 {counts['passed']}｜失败 {counts['failed']}｜异常 {counts['error']}｜跳过 {counts['skipped']}",
        f"- 用例耗时：{total_duration} s",
    ]

    if failed_cases:
        lines.extend(["", "#### 未通过用例"])
        for case in failed_cases[:MAX_FAILED_CASES]:
            status_text = "失败" if case["status"] == "failed" else "异常"
            lines.append(f"- {case['title']}（{status_text}）")
        if len(failed_cases) > MAX_FAILED_CASES:
            lines.append(f"- ……其余 {len(failed_cases) - MAX_FAILED_CASES} 条见报告")

    if report_path:
        report_base_url = get_report_base_url()
        if report_base_url:
            report_url = f"{report_base_url}/{quote(Path(report_path).name)}"
            lines.extend(["", f"- 测试报告：[点击查看]({report_url})"])
        else:
            lines.extend(["", f"- 本地报告：`{report_path}`"])

    if image_url:
        lines.extend(["", f"![report]({image_url})"])

    return "\n".join(lines)


def send_dingtalk_notification(report_path=None):
    project_config = get_project_config()
    webhook = (project_config.get("dingtalk_webhook") or "").strip()
    if not webhook:
        return

    markdown_text = build_dingtalk_markdown(report_path)
    if not markdown_text:
        return

    payload = {
        "msgtype": "markdown",
        "markdown": {
            "title": project_config.get("dingtalk_keyword", "自动化告警"),
            "text": markdown_text,
        },
    }
    logger = get_logger()
    try:
        result = requests.post(webhook, json=payload, timeout=10).json()
    except Exception as exc:
        logger.warning("钉钉通知发送失败: %s", exc)
        return
    if result.get("errcode") != 0:
        logger.warning("钉钉通知发送失败: %s", result)
