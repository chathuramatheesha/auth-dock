# Error Messages
ERR_INVALID_CREDENTIALS = "Invalid email or password."
ERR_VERIFY_EMAIL = "Please verify your email before logging in."
ERR_ACCOUNT_DEACTIVATED = (
    "Your account has been deactivated. Please contact support to regain access."
)
ERR_ACCOUNT_DELETED = "Your account has been deleted. Please contact support."
ERR_USER_ALREADY_VERIFIED = "Your email has already been verified."
ERR_USER_LOGOUT = "Token revoked: user logged out. Please login again."

ERR_EMAIL_TOKEN_USED = "This verification link has already been used."
ERR_INVALID_TOKEN = "Invalid token."
ERR_TOKEN_REVOKED = "Token Revoked: {reason}"
ERR_TOKEN_UNAUTHORIZED = (
    "Unauthorized: Device or IP address does not match the original session."
)
ERR_TOKEN_TYPE_INVALID = (
    "Invalid token type: {token_type}. Expected one of: {token_type_list}"
)

# Success Messages
SUC_EMAIL_VERIFIED = "Your email has been successfully verified."
SUC_LOGOUT = "You have been logged out successfully."
SUC_VERIFICATION_EMAIL_SENT = (
    "A verification email has been sent. Please check your inbox and spam folder."
)
SUC_REGISTRATION = (
    "Registration successful! Please verify your email to activate your account. "
    "If you don't see the email in your inbox, check your spam folder."
)
SUC_RESENT_VERIFICATION_EMAIL = "A new verification link has been sent to your email. Please check both your inbox and spam folder."
