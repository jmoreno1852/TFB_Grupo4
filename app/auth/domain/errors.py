from app.core.errors import DomainError

#Possible authentication errors
class InvalidCredentialsError(DomainError):
    """Error raised when credentials do not match user records"""
    pass

class UserAlreadyExistsError(DomainError):
    """Error raised when trying to register with an already existing user"""
    pass

class TokenInvalidError(DomainError):
    """Error raised when provided token is invalid when authenticating"""
    pass

class UnauthorizedError(DomainError):
    """Error raises when user is not authorized to access a resource or perform an action"""
    pass