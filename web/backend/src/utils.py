
import functools
import enum


def log_trace(message:str) -> None:
    print(message)

# Decorator used to log errors
def error(default=None, message:str=None):
    def decorator(func):
        """Retrieve Error or object"""
        @functools.wraps(wrapped=func)
        def wrapper(*args, **kwargs):
            try:
                result = func(*args, **kwargs)
            except Exception as e:
                if message == None:
                    args_repr: list[str] = [repr(a) for a in args]
                    kwargs_repr: list[str] = [f"{k}={repr(v)}" for k, v in kwargs.items()]
                    signature: str = ", ".join(args_repr + kwargs_repr)
                    message: str = f"Calling {func.__name__}({signature}) \n {e}"
                log_trace(message)
                result = default
            return result
        return wrapper
    return decorator
