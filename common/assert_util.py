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


def assert_business_success(response_json, expected_codes=None):
    """
    兼容常见业务成功字段，避免不同项目返回结构不一致时难维护。
    expected_codes 不传时，如果没有明确业务成功标准，则不强制失败。
    """
    if not isinstance(response_json, dict):
        return

    if "success" in response_json:
        assert response_json["success"] is True, f"业务断言失败：{response_json}"
        return

    if "code" in response_json and expected_codes:
        expected_code_set = {str(code) for code in expected_codes}
        assert str(response_json["code"]) in expected_code_set, (
            f"业务断言失败：{response_json}"
        )


def assert_json_value(response_json, key_path, expected_value):
    actual_value = response_json
    for key in key_path.split("."):
        if not isinstance(actual_value, dict) or key not in actual_value:
            raise AssertionError(
                f"字段断言失败，未找到字段：{key_path}，实际响应：{response_json}"
            )
        actual_value = actual_value[key]

    assert actual_value == expected_value, (
        f"字段断言失败，字段：{key_path}，期望：{expected_value}，实际：{actual_value}"
    )


def assert_contains_keys(response_json, expected_keys):
    for key_path in expected_keys:
        current_value = response_json
        for key in key_path.split("."):
            if not isinstance(current_value, dict) or key not in current_value:
                raise AssertionError(
                    f"字段缺失断言失败，未找到字段：{key_path}，实际响应：{response_json}"
                )
            current_value = current_value[key]
