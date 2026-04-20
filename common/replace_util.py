import re

from common.context_util import test_context


PLACEHOLDER_PATTERN = re.compile(r"\{\{(.*?)\}\}")


def replace_data(data):
    if isinstance(data, dict):
        return {key: replace_data(value) for key, value in data.items()}

    if isinstance(data, list):
        return [replace_data(item) for item in data]

    if isinstance(data, str):
        matches = PLACEHOLDER_PATTERN.findall(data)
        result = data
        for match in matches:
            value = test_context.get(match.strip(), "")
            result = result.replace(f"{{{{{match}}}}}", str(value))
        return result

    return data
