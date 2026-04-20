from pathlib import Path

import requests

from common.config_util import get_project_config
from common.report_util import get_test_case_results


def build_dingtalk_markdown():
    project_config = get_project_config()
    keyword = project_config.get("dingtalk_keyword", "自动化告警")
    image_url = project_config.get("dingtalk_image_url", "")

    cases = get_test_case_results()
    failed_cases = [case for case in cases if case["status"] in {"failed", "error"}]
    if not failed_cases:
        return None

    summary_lines = [
        f"### {keyword}",
        "",
        f"- 项目：{project_config.get('project_name', '接口自动化测试')}",
        f"- 总用例：{len(cases)}",
        f"- 失败/异常：{len(failed_cases)}",
        "",
        "#### 失败用例",
    ]

    for case in failed_cases[:10]:
        summary_lines.append(f"- {case['title']} | {case['status']}")

    report_files = sorted(
        Path("reports").glob("*测试报告.html"),
        key=lambda path: path.stat().st_mtime,
        reverse=True,
    )
    if report_files:
        summary_lines.extend(
            [
                "",
                f"- 本地报告：`{report_files[0]}`",
            ]
        )

    if image_url:
        summary_lines.extend(
            [
                "",
                f"![report]({image_url})",
            ]
        )

    return "\n".join(summary_lines)


def send_dingtalk_notification():
    project_config = get_project_config()
    webhook = project_config.get("dingtalk_webhook", "").strip()
    if not webhook:
        return

    markdown_text = build_dingtalk_markdown()
    if not markdown_text:
        return

    payload = {
        "msgtype": "markdown",
        "markdown": {
            "title": project_config.get("dingtalk_keyword", "自动化告警"),
            "text": markdown_text,
        },
    }
    requests.post(webhook, json=payload, timeout=10)
