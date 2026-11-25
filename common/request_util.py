import json

import allure
import requests
from requests import RequestException

from common.auth_util import build_auth_headers
from common.config_util import get_base_url, get_default_headers, get_project_config
from common.logger_util import get_logger
from common.report_util import add_api_record
from common.replace_util import replace_data


class HttpClient:
    def __init__(self):
        self.session = requests.Session()
        # Local mock endpoints must bypass shell/system proxy settings.
        self.session.trust_env = False
        self.logger = get_logger()
        self.timeout = get_project_config().get("timeout", 10)

    def send(self, method, url, **kwargs):
        url = replace_data(url)
        full_url = url if url.startswith("http") else f"{get_base_url()}{url}"
        headers = {
            **get_default_headers(),
            **build_auth_headers(),
            **replace_data(kwargs.pop("headers", None) or {}),
        }

        for key in ("json", "params", "data"):
            if key in kwargs:
                kwargs[key] = replace_data(kwargs[key])

        request_body = json.dumps(
            kwargs.get("json", kwargs.get("data", kwargs.get("params", {}))),
            ensure_ascii=False,
            indent=2,
            default=str,
        )
        headers_text = json.dumps(headers, ensure_ascii=False, indent=2)

        self.logger.info("请求地址: %s", full_url)
        self.logger.info("请求方式: %s", method.upper())
        self.logger.info("请求头: %s", headers)
        self.logger.info("请求参数: %s", request_body)
        allure.attach(
            request_body,
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
                    "headers": headers_text,
                    "request_body": request_body,
                    "response_body": str(exc),
                    "status_code": "request_error",
                    "elapsed_ms": "",
                }
            )
            raise AssertionError(
                f"接口请求失败，请检查网络、域名、环境或代理配置。原始异常：{exc}"
            ) from exc

        elapsed_ms = int(response.elapsed.total_seconds() * 1000)
        self.logger.info("响应状态码: %s", response.status_code)
        self.logger.info("响应耗时(ms): %s", elapsed_ms)
        self.logger.info("响应内容: %s", response.text)

        allure.attach(
            f"{response.status_code}",
            name="status_code",
            attachment_type=allure.attachment_type.TEXT,
        )
        allure.attach(
            f"{elapsed_ms}",
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
                "headers": headers_text,
                "request_body": request_body,
                "response_body": response.text,
                "status_code": response.status_code,
                "elapsed_ms": elapsed_ms,
            }
        )
        return response

    def close(self):
        self.session.close()
