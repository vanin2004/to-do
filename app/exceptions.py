class BaseAppException(Exception):
    """Base exception for the application."""
    pass

class TodoListNotFoundException(BaseAppException):
    """Exception raised when a todo list is not found."""
    pass

class TodoTaskNotFoundException(BaseAppException):
    """Exception raised when a todo task is not found."""
    pass