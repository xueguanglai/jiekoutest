LOGIN_BY_PASSWORD = "/smartApi/juranApp/login"


def build_password_login_body(
    phone="18350000000",
    password="65a0ec385ca6a0c1e20d1f8270c28303",
    area_code="86",
    slider_code="",
    sign_key="f4c9f2e1256ac58852ff5d9ceea72b7a",
    login_type=2,
):
    return {
        "areaCode": area_code,
        "phone": phone,
        "password": password,
        "sliderCode": slider_code,
        "signKey": sign_key,
        "loginType": login_type,
    }
