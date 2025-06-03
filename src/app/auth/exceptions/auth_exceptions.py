from fastapi import HTTPException, status

from app.auth.constants import auth_constants

# Credentials
auth_invalid_credentials_exception = HTTPException(
    status_code=status.HTTP_403_FORBIDDEN,
    detail=auth_constants.ERR_AUTH_INVALID_CREDENTIALS,
)

# Account
auth_deactivate_account_exception = HTTPException(
    status_code=status.HTTP_403_FORBIDDEN,
    detail=auth_constants.ERR_ACCOUNT_DEACTIVATED,
)

auth_deleted_account_exception = HTTPException(
    status_code=status.HTTP_403_FORBIDDEN,
    detail=auth_constants.ERR_ACCOUNT_DELETED,
)

# Email
auth_verify_email_exception = HTTPException(
    status_code=status.HTTP_403_FORBIDDEN,
    detail=auth_constants.ERR_AUTH_VERIFY_EMAIL,
)

auth_user_already_verified_exception = HTTPException(
    status_code=status.HTTP_400_BAD_REQUEST,
    detail=auth_constants.ERR_USER_ALREADY_VERIFIED,
)

# Tokens
auth_token_invalid_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail=auth_constants.ERR_INVALID_TOKEN,
)

auth_email_token_already_used_exception = HTTPException(
    status_code=status.HTTP_400_BAD_REQUEST,
    detail=auth_constants.SUC_VERIFICATION_EMAIL_SENT,
)

auth_token_revoked_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail=auth_constants.ERR_TOKEN_REVOKED,
    headers={"WWW-Authenticate": "Bearer"},
)
