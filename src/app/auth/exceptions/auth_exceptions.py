from fastapi import HTTPException, status

from app.auth.constants import auth_constants

# Credentials
auth_invalid_credentials_exception = HTTPException(
    status_code=status.HTTP_403_FORBIDDEN,
    detail=auth_constants.AUTH_INVALID_CREDENTIALS_ERROR,
)

# Account
auth_deactivate_account_exception = HTTPException(
    status_code=status.HTTP_403_FORBIDDEN,
    detail=auth_constants.AUTH_DEACTIVATE_ACCOUNT_ERROR,
)

auth_deleted_account_exception = HTTPException(
    status_code=status.HTTP_404_NOT_FOUND,
    detail=auth_constants.AUTH_DELETED_ACCOUNT_ERROR,
)

# Email
auth_verify_email_exception = HTTPException(
    status_code=status.HTTP_403_FORBIDDEN,
    detail=auth_constants.AUTH_VERIFY_EMAIL_ERROR,
)

auth_user_already_verified_exception = HTTPException(
    status_code=status.HTTP_400_BAD_REQUEST,
    detail=auth_constants.AUTH_USER_ALREADY_VERIFIED_ERROR,
)

# Tokens
auth_token_invalid_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail=auth_constants.AUTH_TOKEN_INVALID_ERROR,
)

auth_email_token_already_used_exception = HTTPException(
    status_code=status.HTTP_400_BAD_REQUEST,
    detail=auth_constants.AUTH_EMAIL_TOKEN_ALREADY_USED_ERROR,
)

auth_token_revoked_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail=auth_constants.AUTH_TOKEN_REVOKER_ERROR,
    headers={"WWW-Authenticate": "Bearer"},
)
