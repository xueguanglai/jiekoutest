from common.assert_util import (
    assert_business_code,
    assert_contains_keys,
    assert_json_value,
    assert_response_is_json,
    assert_status_code,
)
from common.extract_util import extract_to_context
from common.replace_util import replace_data


def validate_response(response, case):
    assert_status_code(response, case.get("expected_status_code", 200))
    assert_response_is_json(response)

    response_json = response.json()
    assert_business_code(response_json, case.get("expected_business_codes"))

    expected_values = replace_data(case.get("expected_values") or {})
    for key_path, expected_value in expected_values.items():
        assert_json_value(response_json, key_path, expected_value)

    assert_contains_keys(response_json, case.get("expected_keys") or [])
    return response_json


def validate_and_extract(response, case):
    response_json = validate_response(response, case)
    extract_to_context(response_json, case.get("extract"))
    return response_json
