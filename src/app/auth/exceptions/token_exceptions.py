from fastapi import HTTPException, status

from ..constants import token_constants

token_refresh_save_exception = HTTPException(
    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
    detail=token_constants.TOKEN_REFRESH_SAVE_FAILED_ERROR,
)

blacklisted_token_save_exception = HTTPException(
    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
    detail=token_constants.BLACKLISTED_TOKEN_SAVE_FAILED_ERROR,
)

blacklisted_token_update_exception = HTTPException(
    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
    detail=token_constants.BLACKLISTED_TOKEN_UPDATE_FAILED_ERROR,
)

jwt_credentials_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail=token_constants.JWT_CREDENTIALS_INVALID,
    headers={"WWW-Authenticate": "Bearer"},
)

jwt_token_expired_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail=token_constants.JWT_TOKEN_EXPIRED,
    headers={"WWW-Authenticate": "Bearer"},
)

jwt_token_invalid_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail=token_constants.JWT_TOKEN_INVALID,
    headers={"WWW-Authenticate": "Bearer"},
)

jwt_token_invalid_type_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail=token_constants.JWT_INVALID_TOKEN_TYPE,
    headers={"WWW-Authenticate": "Bearer"},
)
