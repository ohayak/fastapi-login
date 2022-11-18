from fastapi import HTTPException, status
from httpx import Response


class ServiceError(HTTPException):
    """
    This exception can be returned from handler as is.
    If this exception is raised you can skip handling.

    Your application will return normal response
     with status_code=400 and human-readable message.
    """

    def __init__(self, action: str, service_response: Response) -> None:
        try:
            error_data = service_response.json()
        except LookupError:
            error_data = service_response.text
        self.detail = f"Can't {action}. Getter respond: {error_data}" f" (status code: {service_response.status_code})"
        self.response = service_response
        self.status_code = 400


class InternalServerError(HTTPException):
    def __init__(self) -> None:
        super().__init__(status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error!")


class InputValidationError(HTTPException):
    def __init__(self, schema_err) -> None:
        super().__init__(status.HTTP_400_BAD_REQUEST, detail="inputs provided are not valid: %s" % schema_err)


class NotFoundError(HTTPException):
    def __init__(self, resouce) -> None:
        super().__init__(status.HTTP_404_NOT_FOUND, detail="resource %s not found" % resouce)


class AlreadyExistsError(HTTPException):
    def __init__(self, resouce) -> None:
        super().__init__(status.HTTP_409_CONFLICT, detail="resource %s already exists" % resouce)
