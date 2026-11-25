from common.config_util import get_project_config
from common.extract_util import get_value_by_path


def assert_status_code(response, expected_code=200):
    actual_code = response.status_code
    assert actual_code == expected_code, (
        f"状态码断言失败，期望：{expected_code}，实际：{actual_code}"
    )


def assert_response_is_json(response):
    try:
        response.json()
    except Exception as exc:
        raise AssertionError(f"响应结果不是 JSON：{response.text}") from exc


def assert_business_code(response_json, expected_codes=None):
    """
    写了 expected_business_codes 就严格校验业务码字段（字段名见 project.yaml 的 business_code_field）。
    没写时，仅当响应里有 success 字段才校验其为 True。
    """
    if not isinstance(response_json, dict):
        return

    if expected_codes:
        code_field = get_project_config().get("business_code_field", "code")
        assert code_field in response_json, (
            f"业务码断言失败，响应中没有 {code_field} 字段：{response_json}"
        )
        expected_code_set = {str(code) for code in expected_codes}
        assert str(response_json[code_field]) in expected_code_set, (
            f"业务码断言失败，期望：{sorted(expected_code_set)}，实际响应：{response_json}"
        )
        return

    if "success" in response_json:
        assert response_json["success"] is True, f"业务断言失败：{response_json}"


def assert_json_value(response_json, key_path, expected_value):
    # data.list.*.status 表示列表的每一项都要满足，且列表不能为空。
    prefix, wildcard, rest = str(key_path).partition(".*")
    if wildcard:
        try:
            items = get_value_by_path(response_json, prefix)
        except KeyError as exc:
            raise AssertionError(
                f"字段断言失败，未找到字段：{prefix}，实际响应：{response_json}"
            ) from exc
        assert isinstance(items, list) and items, (
            f"字段断言失败，{prefix} 应为非空列表，实际：{items!r}"
        )
        for index in range(len(items)):
            assert_json_value(response_json, f"{prefix}.{index}{rest}", expected_value)
        return

    try:
        actual_value = get_value_by_path(response_json, key_path)
    except KeyError as exc:
        raise AssertionError(
            f"字段断言失败，未找到字段：{key_path}，实际响应：{response_json}"
        ) from exc

    assert actual_value == expected_value, (
        f"字段断言失败，字段：{key_path}，期望：{expected_value!r}，实际：{actual_value!r}"
    )


def assert_contains_keys(response_json, expected_keys):
    for key_path in expected_keys:
        try:
            get_value_by_path(response_json, key_path)
        except KeyError as exc:
            raise AssertionError(
                f"字段缺失断言失败，未找到字段：{key_path}，实际响应：{response_json}"
            ) from exc
