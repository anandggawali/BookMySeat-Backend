from schemas.base_response import BaseResponse


def success_response(
    data=None,
    message="Success",
    status=200
):
    return BaseResponse(
        status=status,
        message=message,
        errorMessage="",
        data=data
    )


def error_response(
    message="Failed",
    error="",
    status=400
):
    return BaseResponse(
        status=status,
        message=message,
        errorMessage=error,
        data=None
    )