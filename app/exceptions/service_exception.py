from app.exceptions.custom_exception import CustomException


class ServiceException(CustomException):
    def __init__(self, status_code: int = 500, detail: str = "Service error", additional_info: dict = None):
        super().__init__(status_code=status_code, detail=detail,
                         exception_type="ServiceException", additional_info=additional_info)
