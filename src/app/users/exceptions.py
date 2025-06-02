from fastapi import status, HTTPException

from . import constants

user_email_already_exists_exception = HTTPException(
    status_code=status.HTTP_409_CONFLICT,
    detail=constants.ERR_USER_EMAIL_ALREADY_EXISTS,
)

user_creation_failed_exception = HTTPException(
    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
    detail=constants.ERR_USER_CREATION_FAILED,
)

user_update_failed_exception = HTTPException(
    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
    detail=constants.ERR_USER_UPDATE_FAILED,
)

user_id_not_found_exception = HTTPException(
    status_code=status.HTTP_404_NOT_FOUND,
    detail=constants.ERR_USER_ID_NOT_FOUND,
)

user_email_not_found_exception = HTTPException(
    status_code=status.HTTP_404_NOT_FOUND,
    detail=constants.ERR_USER_EMAIL_NOT_FOUND,
)

user_not_found_exception = HTTPException(
    status_code=status.HTTP_404_NOT_FOUND,
    detail=constants.ERR_USER_NOT_FOUND,
)
