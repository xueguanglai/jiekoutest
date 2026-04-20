import json

import allure
import requests
from requests import RequestException

from common.auth_util import get_token
from common.config_util import get_base_url, get_default_headers, get_project_config
from common.logger_util import get_logger
from common.report_util import add_api_record
from common.replace_util import replace_data


class HttpClient:
    def __init__(self):
        self.session = requests.Session()
        self.logger = get_logger()
        project_config = get_project_config()
        self.timeout = project_config.get("timeout", 10)

    def send(self, method, url, **kwargs):
        full_url = url if url.startswith("http") else f"{get_base_url()}{url}"
        headers = get_default_headers().copy()
        custom_headers = kwargs.pop("headers", {})
        headers.update(custom_headers)
        auto_token = get_token()
        auth_header_name = get_project_config().get("token_header_name", "Authorization")
        auth_prefix = get_project_config().get("token_prefix", "Bearer")
        if auto_token and auth_header_name not in headers:
            headers[auth_header_name] = (
                f"{auth_prefix} {auto_token}".strip()
                if auth_prefix
                else auto_token
            )

        if "json" in kwargs:
            kwargs["json"] = replace_data(kwargs["json"])
        if "params" in kwargs:
            kwargs["params"] = replace_data(kwargs["params"])
        if "data" in kwargs:
            kwargs["data"] = replace_data(kwargs["data"])

        self.logger.info("请求地址: %s", full_url)
        self.logger.info("请求方式: %s", method.upper())
        self.logger.info("请求头: %s", headers)

        if "json" in kwargs:
            self.logger.info(
                "请求体: %s",
                json.dumps(kwargs["json"], ensure_ascii=False, indent=2),
            )
            allure.attach(
                json.dumps(kwargs["json"], ensure_ascii=False, indent=2),
                name="request_body",
                attachment_type=allure.attachment_type.JSON,
            )

        try:
            response = self.session.request(
                method=method,
                url=full_url,
                headers=headers,
                timeout=kwargs.pop("timeout", self.timeout),
                **kwargs,
            )
        except RequestException as exc:
            self.logger.error("请求异常: %s", exc)
            allure.attach(
                str(exc),
                name="request_exception",
                attachment_type=allure.attachment_type.TEXT,
            )
            add_api_record(
                {
                    "api_title": full_url,
                    "method": method.upper(),
                    "url": full_url,
                    "headers": json.dumps(headers, ensure_ascii=False, indent=2),
                    "request_body": json.dumps(kwargs.get("json", kwargs.get("data", {})), ensure_ascii=False, indent=2),
                    "response_body": str(exc),
                    "status_code": "request_error",
                    "elapsed_ms": "",
                }
            )
            raise AssertionError(
                f"接口请求失败，请检查网络、域名、环境或代理配置。原始异常：{exc}"
            ) from exc

        self.logger.info("响应状态码: %s", response.status_code)
        self.logger.info("响应耗时(ms): %s", int(response.elapsed.total_seconds() * 1000))
        self.logger.info("响应内容: %s", response.text)

        allure.attach(
            f"{response.status_code}",
            name="status_code",
            attachment_type=allure.attachment_type.TEXT,
        )
        allure.attach(
            f"{int(response.elapsed.total_seconds() * 1000)}",
            name="elapsed_ms",
            attachment_type=allure.attachment_type.TEXT,
        )
        allure.attach(
            response.text,
            name="response_body",
            attachment_type=allure.attachment_type.TEXT,
        )
        add_api_record(
            {
                "api_title": full_url,
                "method": method.upper(),
                "url": full_url,
                "headers": json.dumps(headers, ensure_ascii=False, indent=2),
                "request_body": json.dumps(kwargs.get("json", kwargs.get("data", {})), ensure_ascii=False, indent=2),
                "response_body": response.text,
                "status_code": response.status_code,
                "elapsed_ms": int(response.elapsed.total_seconds() * 1000),
            }
        )
        return response

    def close(self):
        self.session.close()
