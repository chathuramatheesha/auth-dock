from app.core import ULID


class UserEmailExistsError(Exception):
    def __init__(self, email: str):
        self.email = email


class UserCreateFailedError(Exception):
    def __init__(self, detail: str = "User creation failed"):
        self.detail = detail
        super().__init__(detail)


class UserUpdateFailedError(Exception):
    def __init__(self, detail: str = "User update failed"):
        self.detail = detail
        super().__init__(detail)


class UserNotFoundError(Exception):
    def __init__(self, detail="User not found"):
        self.detail = detail
        super().__init__(detail)


class UserIDNotFoundError(Exception):
    def __init__(self, user_id: ULID):
        self.user_id = user_id
        super().__init__(f"User with ID '{user_id}' not found")


class UserEmailNotFoundError(Exception):
    def __init__(self, email: str):
        self.email = email
        super().__init__(f"User with email '{email}' not found")
