import functools

def log_method_calls(logger):
    """Decorator to log method entry and exit."""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            logger.debug(f"Entering method: {func.__name__} with args: {args}, kwargs: {kwargs}")
            try:
                result = func(*args, **kwargs)
                logger.debug(f"Exiting method: {func.__name__} with result: {result}")
                return result
            except Exception as e:
                logger.exception(f"Exception in method {func.__name__}: {e}")
                raise  # Re-raise the exception after logging
        return wrapper
    return decorator