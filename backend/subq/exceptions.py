from rest_framework.exceptions import APIException


class SubQException(APIException):
    def __init__(self, default_code: str, status_code: int=None, detail: str=None, theraq_err: dict=None):
        self.default_code = default_code
        if theraq_err:
            self.status_code = 500 if theraq_err.get("code") is not None else theraq_err.get("code")
            self.detail = "An Error has occured" if theraq_err.get("message") is not None else theraq_err.get("message")
        else:
            self.status_code = 500 if status_code is None else status_code
            self.detail = "An Error has occured" if detail is None else detail


class SubQFollowerException(APIException):
    def __init__(self, default_code: str, status_code: int=None, detail: str=None, theraq_err: dict=None):
        self.default_code = default_code
        if theraq_err:
            self.status_code = 500 if theraq_err.get("code") is not None else theraq_err.get("code")
            self.detail = "An Error has occured" if theraq_err.get("message") is not None else theraq_err.get("message")
        else:
            self.status_code = 500 if status_code is None else status_code
            self.detail = "An Error has occured" if detail is None else detail
