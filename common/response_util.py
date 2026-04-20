from common.assert_util import (
    assert_business_success,
    assert_contains_keys,
    assert_json_value,
    assert_response_is_json,
    assert_status_code,
)
from common.extract_util import extract_to_context
def validate_response(response, case):
    assert_status_code(response, case["expected_status_code"])
    assert_response_is_json(response)

    response_json = response.json()
    assert_business_success(response_json, case.get("expected_business_codes"))

    expected_values = case.get("expected_values", {})
    for key_path, expected_value in expected_values.items():
        assert_json_value(response_json, key_path, expected_value)

    expected_keys = case.get("expected_keys", [])
    if expected_keys:
        assert_contains_keys(response_json, expected_keys)

    return response_json


def validate_and_extract(response, case):
    response_json = validate_response(response, case)
    extract_to_context(response_json, case.get("extract"))
    return response_json
