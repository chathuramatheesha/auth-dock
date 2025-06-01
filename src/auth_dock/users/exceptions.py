from fastapi import status, HTTPException

from . import constants

user_email_already_exists_exception = HTTPException(
    status_code=status.HTTP_409_CONFLICT,
    detail=constants.USER_EMAIL_ALREADY_EXISTS_ERROR,
)

user_creation_failed_exception = HTTPException(
    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
    detail=constants.USER_CREATION_FAILED_ERROR,
)

user_update_failed_exception = HTTPException(
    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
    detail=constants.USER_UPDATE_FAILED_ERROR,
)

user_password_hashing_exception = HTTPException(
    status_code=status.HTTP_400_BAD_REQUEST,
    detail=constants.USER_PASSWORD_INVALID_ERROR,
)

user_id_not_exists_exception = HTTPException(
    status_code=status.HTTP_404_NOT_FOUND,
    detail=constants.USER_ID_NOT_EXISTS_ERROR,
)

user_email_not_exists_exception = HTTPException(
    status_code=status.HTTP_404_NOT_FOUND,
    detail=constants.USER_EMAIL_NOT_EXISTS_ERROR,
)

user_not_found_exception = HTTPException(
    status_code=status.HTTP_404_NOT_FOUND,
    detail=constants.USER_NOT_FOUND_ERROR,
)
