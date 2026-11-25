import re

from common.context_util import test_context


PLACEHOLDER_PATTERN = re.compile(r"\{\{\s*([^{}]+?)\s*\}\}")
_MISSING = object()


def _lookup(name):
    value = test_context.get(name, _MISSING)
    if value is _MISSING:
        raise AssertionError(
            f"占位符 {{{{{name}}}}} 没有值，请确认上游用例已执行并通过 extract 提取了该变量"
        )
    return value


def replace_data(data):
    if isinstance(data, dict):
        return {key: replace_data(value) for key, value in data.items()}

    if isinstance(data, list):
        return [replace_data(item) for item in data]

    if isinstance(data, str):
        full_match = PLACEHOLDER_PATTERN.fullmatch(data)
        if full_match:
            return _lookup(full_match.group(1))
        return PLACEHOLDER_PATTERN.sub(lambda match: str(_lookup(match.group(1))), data)

    return data
