import html
from datetime import datetime


CURRENT_TEST_ID = None
TEST_API_RECORDS = {}
TEST_CASE_RESULTS = []


def set_current_test(test_id):
    global CURRENT_TEST_ID
    CURRENT_TEST_ID = test_id
    TEST_API_RECORDS.setdefault(test_id, [])


def clear_current_test():
    global CURRENT_TEST_ID
    CURRENT_TEST_ID = None


def add_api_record(record):
    if not CURRENT_TEST_ID:
        return
    TEST_API_RECORDS.setdefault(CURRENT_TEST_ID, []).append(record)


def pop_api_records(test_id):
    return TEST_API_RECORDS.pop(test_id, [])


def add_test_case_result(result):
    TEST_CASE_RESULTS.append(result)


def clear_test_case_results():
    TEST_CASE_RESULTS.clear()


def get_test_case_results():
    return list(TEST_CASE_RESULTS)


def _build_summary(cases):
    total = len(cases)
    passed = sum(1 for case in cases if case["status"] == "passed")
    failed = sum(1 for case in cases if case["status"] == "failed")
    skipped = sum(1 for case in cases if case["status"] == "skipped")
    error = sum(1 for case in cases if case["status"] == "error")
    return {
        "total": total,
        "passed": passed,
        "failed": failed,
        "skipped": skipped,
        "error": error,
    }


def _status_text(status):
    mapping = {
        "passed": "通过",
        "failed": "失败",
        "skipped": "跳过",
        "error": "异常",
    }
    return mapping.get(status, status)


def build_custom_html_report(report_title, cases):
    summary = _build_summary(cases)
    generated_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    case_blocks = []
    for index, case in enumerate(cases, start=1):
        case_title = html.escape(case.get("title", f"用例{index}"))
        case_status = _status_text(case.get("status", ""))
        case_nodeid = html.escape(case.get("nodeid", ""))
        case_duration = html.escape(str(case.get("duration", "")))
        case_error = html.escape(case.get("error_message", ""))

        api_blocks = []
        for api_index, record in enumerate(case.get("api_records", []), start=1):
            method = html.escape(str(record.get("method", "")))
            url = html.escape(str(record.get("url", "")))
            headers = html.escape(str(record.get("headers", "")))
            request_body = html.escape(str(record.get("request_body", "")))
            response_body = html.escape(str(record.get("response_body", "")))
            status_code = html.escape(str(record.get("status_code", "")))
            elapsed_ms = html.escape(str(record.get("elapsed_ms", "")))
            api_title = html.escape(str(record.get("api_title", f"接口{api_index}")))

            api_blocks.append(
                f"""
                <details class="api-card">
                    <summary class="api-summary">
                        <span class="api-title">{api_title}</span>
                        <span class="api-badge">{method}</span>
                        <span class="api-badge">状态 {status_code}</span>
                        <span class="api-badge">{elapsed_ms} ms</span>
                    </summary>
                    <div class="api-content">
                        <div class="kv"><span>请求方式</span><strong>{method}</strong></div>
                        <div class="kv"><span>请求地址</span><strong>{url}</strong></div>
                        <div class="kv"><span>请求状态</span><strong>{status_code}</strong></div>
                        <div class="kv"><span>响应耗时</span><strong>{elapsed_ms} ms</strong></div>
                        <div class="section-title">请求头</div>
                        <pre>{headers}</pre>
                        <div class="section-title">请求体</div>
                        <pre>{request_body}</pre>
                        <div class="section-title">响应结果</div>
                        <pre>{response_body}</pre>
                    </div>
                </details>
                """
            )

        if not api_blocks:
            api_blocks.append('<div class="empty">当前用例没有记录到接口请求数据。</div>')

        error_block = ""
        if case_error:
            error_block = f"""
            <div class="error-box">
                <div class="section-title">失败信息</div>
                <pre>{case_error}</pre>
            </div>
            """

        case_blocks.append(
            f"""
            <details class="case-card status-{case.get("status", "")}">
                <summary class="case-summary">
                    <div class="case-header">
                        <div>
                            <div class="case-index">用例 {index}</div>
                            <h2>{case_title}</h2>
                            <div class="case-nodeid">{case_nodeid}</div>
                        </div>
                        <div class="case-meta">
                            <div><span>结果</span><strong>{case_status}</strong></div>
                            <div><span>耗时</span><strong>{case_duration} s</strong></div>
                        </div>
                    </div>
                </summary>
                <div class="case-content">
                    {error_block}
                    <div class="api-list">
                        {''.join(api_blocks)}
                    </div>
                </div>
            </details>
            """
        )

    return f"""
    <!DOCTYPE html>
    <html lang="zh-CN">
    <head>
        <meta charset="UTF-8">
        <title>{html.escape(report_title)}</title>
        <style>
            body {{
                margin: 0;
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
                background: #f5f7fb;
                color: #1f2937;
            }}
            .container {{
                max-width: 1280px;
                margin: 0 auto;
                padding: 32px 20px 60px;
            }}
            .hero {{
                background: linear-gradient(135deg, #0f172a, #1d4ed8);
                color: #fff;
                border-radius: 16px;
                padding: 28px;
                margin-bottom: 24px;
            }}
            .hero h1 {{
                margin: 0 0 12px 0;
                font-size: 30px;
            }}
            .hero p {{
                margin: 0;
                opacity: 0.9;
            }}
            .summary {{
                display: grid;
                grid-template-columns: repeat(5, minmax(120px, 1fr));
                gap: 12px;
                margin: 24px 0;
            }}
            .summary-card {{
                background: #fff;
                border-radius: 12px;
                padding: 16px;
                box-shadow: 0 4px 14px rgba(15, 23, 42, 0.06);
            }}
            .summary-card span {{
                display: block;
                color: #64748b;
                font-size: 13px;
                margin-bottom: 8px;
            }}
            .summary-card strong {{
                font-size: 28px;
            }}
            .case-card {{
                background: #fff;
                border-radius: 16px;
                margin-bottom: 20px;
                box-shadow: 0 6px 18px rgba(15, 23, 42, 0.06);
                border-left: 6px solid #94a3b8;
                overflow: hidden;
            }}
            .status-passed {{ border-left-color: #16a34a; }}
            .status-failed {{ border-left-color: #dc2626; }}
            .status-skipped {{ border-left-color: #ca8a04; }}
            .status-error {{ border-left-color: #7c3aed; }}
            .case-summary {{
                list-style: none;
                cursor: pointer;
                padding: 20px;
            }}
            .case-summary::-webkit-details-marker {{
                display: none;
            }}
            .case-content {{
                padding: 0 20px 20px;
            }}
            .case-header {{
                display: flex;
                justify-content: space-between;
                gap: 16px;
                align-items: flex-start;
            }}
            .case-index {{
                color: #64748b;
                font-size: 13px;
                margin-bottom: 6px;
            }}
            .case-header h2 {{
                margin: 0 0 8px 0;
                font-size: 24px;
            }}
            .case-nodeid {{
                color: #94a3b8;
                font-size: 12px;
                word-break: break-all;
            }}
            .case-meta {{
                min-width: 160px;
                background: #f8fafc;
                border-radius: 12px;
                padding: 12px;
            }}
            .case-meta div {{
                display: flex;
                justify-content: space-between;
                margin-bottom: 8px;
            }}
            .case-meta div:last-child {{
                margin-bottom: 0;
            }}
            .case-meta span {{
                color: #64748b;
            }}
            .api-card {{
                border: 1px solid #e2e8f0;
                border-radius: 12px;
                margin-top: 14px;
                background: #fcfdff;
                overflow: hidden;
            }}
            .api-summary {{
                list-style: none;
                cursor: pointer;
                padding: 16px;
                display: flex;
                flex-wrap: wrap;
                gap: 10px;
                align-items: center;
                background: #f8fafc;
            }}
            .api-summary::-webkit-details-marker {{
                display: none;
            }}
            .api-content {{
                padding: 16px;
                border-top: 1px solid #e2e8f0;
            }}
            .api-title {{
                font-size: 18px;
                font-weight: 700;
                color: #0f172a;
                margin-right: auto;
            }}
            .api-badge {{
                display: inline-flex;
                align-items: center;
                padding: 4px 10px;
                border-radius: 999px;
                background: #e2e8f0;
                color: #334155;
                font-size: 12px;
                font-weight: 600;
            }}
            .kv {{
                display: flex;
                justify-content: space-between;
                gap: 12px;
                padding: 6px 0;
                border-bottom: 1px dashed #e2e8f0;
            }}
            .kv span {{
                color: #64748b;
            }}
            .section-title {{
                margin: 14px 0 8px;
                font-weight: 700;
                color: #334155;
            }}
            pre {{
                margin: 0;
                white-space: pre-wrap;
                word-break: break-word;
                background: #0f172a;
                color: #e2e8f0;
                padding: 14px;
                border-radius: 10px;
                overflow-x: auto;
                font-size: 13px;
                line-height: 1.5;
            }}
            .error-box {{
                margin-top: 12px;
                background: #fff1f2;
                border: 1px solid #fecdd3;
                border-radius: 12px;
                padding: 14px;
            }}
            .empty {{
                padding: 16px;
                color: #64748b;
                background: #f8fafc;
                border-radius: 12px;
                margin-top: 12px;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="hero">
                <h1>{html.escape(report_title)}</h1>
                <p>生成时间：{generated_time}</p>
            </div>
            <div class="summary">
                <div class="summary-card"><span>总用例</span><strong>{summary["total"]}</strong></div>
                <div class="summary-card"><span>通过</span><strong>{summary["passed"]}</strong></div>
                <div class="summary-card"><span>失败</span><strong>{summary["failed"]}</strong></div>
                <div class="summary-card"><span>跳过</span><strong>{summary["skipped"]}</strong></div>
                <div class="summary-card"><span>异常</span><strong>{summary["error"]}</strong></div>
            </div>
            {''.join(case_blocks)}
        </div>
    </body>
    </html>
    """
