from common.context_util import test_context


TOKEN_KEY_CANDIDATES = ("jwtToken", "token", "accessToken", "access_token")


def get_token():
    for key in TOKEN_KEY_CANDIDATES:
        value = test_context.get(key)
        if value:
            return value
    return None
