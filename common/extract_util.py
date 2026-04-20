from common.context_util import test_context


def get_value_by_path(data, key_path):
    current = data
    for key in key_path.split("."):
        if isinstance(current, dict) and key in current:
            current = current[key]
            continue
        raise KeyError(f"未找到字段：{key_path}")
    return current


def extract_to_context(response_json, extract_rules=None):
    if not extract_rules:
        return {}

    extracted_data = {}
    for context_key, response_path in extract_rules.items():
        try:
            extracted_data[context_key] = get_value_by_path(response_json, response_path)
        except KeyError:
            continue

    if extracted_data:
        test_context.update(extracted_data)
    return extracted_data
