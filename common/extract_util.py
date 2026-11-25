from common.context_util import test_context


def get_value_by_path(data, key_path):
    """按 a.b.0.c 形式取值，数字段可作为列表下标。"""
    current = data
    for key in str(key_path).split("."):
        if isinstance(current, dict) and key in current:
            current = current[key]
        elif (
            isinstance(current, list)
            and key.lstrip("-").isdigit()
            and -len(current) <= int(key) < len(current)
        ):
            current = current[int(key)]
        else:
            raise KeyError(f"未找到字段：{key_path}")
    return current


def extract_to_context(response_json, extract_rules=None):
    if not extract_rules:
        return {}

    extracted_data = {}
    for context_key, response_path in extract_rules.items():
        try:
            extracted_data[context_key] = get_value_by_path(response_json, response_path)
        except KeyError as exc:
            raise AssertionError(
                f"变量提取失败：{context_key} <- {response_path}，实际响应：{response_json}"
            ) from exc

    test_context.update(extracted_data)
    return extracted_data
