from fastapi import HTTPException


class CustomHTTPException(HTTPException):
    def __init__(self, status_code: int, detail: str, exception_type: str = None, additional_info: dict = None):
        super().__init__(status_code=status_code, detail=detail)
        self.exception_type = exception_type or 'CustomHTTPException'
        self.additional_info = additional_info or {}


class CustomException(Exception):
    def __init__(self, status_code: int, detail: str, exception_type: str, additional_info: dict = None):
        self.status_code = status_code
        self.detail = detail
        self.exception_type = exception_type
        self.additional_info = additional_info or {}


class DatabaseException(CustomException):
    def __init__(self, status_code: int = 500, detail: str = "Database error", additional_info: dict = None):
        super().__init__(status_code=status_code, detail=detail,
                         exception_type="DatabaseException", additional_info=additional_info)
